
import io
import json
import logging as log
from fdk import response
import oci
import datetime

def handler(ctx, data: io.BytesIO=None):
    signer = oci.auth.signers.get_resource_principals_signer()
    core_client = oci.core.ComputeClient(config={}, signer=signer)
    #these are defaults if we are unable to establish the Shape from Image name
    v_shape_code = "2.1"
    v_shape_name = "VM.Standard2.1"
    v_assign_pubIP  = False
    global v_instances_sub_id
    # Get the json body 
    try:
        body = json.loads(data.getvalue())
        
        v_name          = body['data']['resourceName']
        v_comp_id       = body['data']['compartmentId']
        v_ad            = body['data']['availabilityDomain']
        v_display_name  = "Instance_" + body['data']['resourceName']
        v_image_id      = body['data']['resourceId']

        log.info("BODY JSON loaded...")
        log.info("BODY {}".format(body))
        log.info("IMAGE NAME: {}".format(v_name))
    except Exception as e:
        raise

    #get the resource name/ file name to decode the shape from
    try:
        #get the string after last "_"
        #this must be in form "digit.digit",  i.e 2.1 => VMStandard 2.1
        #this will be compared with P_SHAPE
        v_shape_code = v_name[v_name.rfind("_")+1:]
        log.info("SHAPE CODE: {}".format(v_shape_code))
    except Exception as e:
        v_shape_code = "2.1"
        log.info("ERROR while getting the shape code from resourceName, will chose {}".format(v_shape_code))
        log.info(e)

    
    try:
        cfg                 = ctx.Config()
        # we expect to find in the config parameter a key p_shapes as below
        # {"shapes":{"2.1":"VM.Standard2.1","2.2":"VM.Standard2.2","2.8":"VM.Standard2.8","2.16":"VM.Standard2.16"}}
        # if this is not set then we chose VM standard 2.1
        log.info("PSHAPE: {}".format(cfg['p_shapes']))
        v_shape_dict        = json.loads(cfg['p_shapes'])
        v_shape_name        = v_shape_dict['shapes'][v_shape_code]
        log.info("SHAPE NAME: {}".format(v_shape_name))

    except Exception as e:
        v_shape_name = "VM.Standard2.1"
        log.info("ERROR while trying to establish the shape, will choose {}".format(v_shape_name))
        log.info(e)

    try:
        # we expect to find in the config parameter a key instances_subnet and the value beign an ocid of a subnet in which the instances will reside
        log.info("Instances subnet id: {}".format(cfg['instances_subnet']))
        v_instances_sub_id = cfg['instances_subnet']
    except Exception as e:
        log.info("ERROR while trying to get the subnet id for instances")
        log.info(e)
 
    
    try:
        log.info("Assign public ip is set to : {}".format(cfg['assign_public_ip']))
        v_assign_pubIP = cfg['assign_public_ip']
    except Exception as e:
        v_assign_pubIP  = False
        log.info("Coult not establish if it should assign public ip, will choose by default {}".format(v_assign_pubIP))
        log.info(e)                             

    launch_instance_response = core_client.launch_instance(
        launch_instance_details=oci.core.models.LaunchInstanceDetails(
            availability_domain     =v_ad,
            compartment_id          = v_comp_id,
            shape                   = v_shape_name,
            create_vnic_details     = oci.core.models.CreateVnicDetails(
                assign_public_ip            = v_assign_pubIP,
                assign_private_dns_record   = False,
                subnet_id                   = v_instances_sub_id
                ),
            display_name            = v_display_name,
            freeform_tags           = {'INST_TYPE': 'FROM_VMDK'},
            #hostname_label="EXAMPLE-hostnameLabel-Value",
            image_id                = v_image_id
        )
    )
    log.info("COMPUTE instance {} is being lauched".format(launch_instance_response.data.display_name))
        
    return("RETURN ",launch_instance_response.data)
