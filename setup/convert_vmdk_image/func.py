
import io
import json
import logging
from fdk import response
import oci
import datetime

def handler(ctx, data: io.BytesIO=None):
    signer = oci.auth.signers.get_resource_principals_signer()
    
    core_client = oci.core.ComputeClient(config={}, signer=signer)
    obj_client = oci.object_storage.ObjectStorageClient(config={}, signer=signer)
    
    body = json.loads(data.getvalue())
    logging.info("BODY json loaded...")
    
    v_bucket_name   = body['data']['additionalDetails']['bucketName']
    v_namespace     = body['data']['additionalDetails']['namespace']
    v_obj_name      = body['data']['resourceName']
    v_bucket_id     = body['data']['additionalDetails']['bucketId']
    v_comp_id       = body['data']['compartmentId']
    v_endpoint      = obj_client.base_client.endpoint # i.e. https://objectstorage.af-johannesburg-1.oraclecloud.com
    v_par           = "PAR_for_import_vmdk_" + v_obj_name
    v_access_type   = "ObjectRead"
    
    logging.info("VARS were set from json...")
    #In case we need to set Function config vars
    cfg     = ctx.Config()

    create_PAR_resp = obj_client.create_preauthenticated_request(
        namespace_name      = v_namespace,
        bucket_name         = v_bucket_name,
        create_preauthenticated_request_details=oci.object_storage.models.CreatePreauthenticatedRequestDetails(
            name            = v_par,
            access_type     = v_access_type,
            time_expires    = datetime.datetime.strptime("2042-11-26T03:00:33.197Z","%Y-%m-%dT%H:%M:%S.%fZ"),
            bucket_listing_action="ListObjects",
            object_name     = v_obj_name))
    
    v_uri = create_PAR_resp.data.access_uri
    logging.info("PAR was created...")
    create_img_response = core_client.create_image(
        create_image_details = oci.core.models.CreateImageDetails(
            display_name            =v_obj_name,
            #compartment_id          = "ocid1.compartment.oc1..aaaaaaaawrkzz3hmmifq65xo6zx7impepmtoekwqyhzzc7dctzmxn75gyjnq",
            compartment_id          = v_comp_id,
            launch_mode             = "NATIVE",
            image_source_details    = oci.core.models.ImageSourceViaObjectStorageUriDetails(
                source_image_type   = "VMDK",
                source_uri          = v_endpoint + v_uri
                ,source_type = "objectStorageUri"
                )
            )
    )
    logging.info("CUSTOM image {} is being created".format(create_img_response.data.display_name))

    return("RETURN ",create_img_response.data)

    #return response.Response(
    #    ctx,
    #    response_data=json.dumps(x.data),
    #    headers={"Content-Type": "application/json"}
    #)
