# SETUP

## Introduction

This deployment is using the OCI Function and Events services to create a Custom Image when a vmdk is uploaded in a designated bucket and then, it will create a Compute Instance from that Custom Image with a VM.Standard2 shape based on the name of the object.

## The deployment contains the following files:

 - convert_vmdk_image > Folder containing the docker image for the function that will convert the vmdk into a Custom Image.
 - create_instance_image > Folder containing the docker image for the function that will create the Compute instance.
 - destroy_setup.yaml > Ansible playbook that will destroy/remove the resources created by the setup playbook.
 - inventory_setup.ini > Inventory file containg the variables for the setup playbook ( you will have to edit the variables).
 - readme.md > Readme file.
 - setup.yaml > Ansible playbook that will create the required resources.


### The setup.yaml playbook will free you from the manual work to deploy the functions and will create the related resources.
It will do the following:

 - Create an authentication token to allow the docker registry login
 - Create a dynamic group for the function service
 - Create the Policies for the dynamic group to read objects from buckets and manage instance-family in your compartment
 - Create a Container Repository
 - It will build both docker images and push them to the Repository
 - Create an application for the functions to reside in
 - Create the two functions (the one for converting the vmdk to Custom Image and the second one for creating the Compute Instance)
 - Create the two event rules (the one that triggers the “convert” function and the second one that triggers the “create compute instance” function)
 - Write the details about the resources created in the “inventory_setup.ini” file to be later used by the “destroy_setup_yaml” when you want to destroy the resources created by this playbook.


## Workflow

 - Upload a vmdk file in a designated bucket.

   The name of the object uploaded must have it's name ending with either _2.1, _2.2, _2.4, _2.8, _2.16, _2.24 . This will be used to set the shape of the Compute Instances.

   ![](./images/ObjectUploaded.png)


 - Whenever you upload a vmdk into a designated bucket, an Event rule is triggered and it will fire a function that will create a Custom Image from that object.
   
   ![](./images/Event1matching.png)
   ![](./images/Event1Actions.png)


 - Then, another event rule is triggered when the Custom Image is created, that will fire another function to create a Compute Instance based on that Custom Image.

   ![](./images/Event2matching.png)
   ![](./images/Event2Actions.png)


 - The shape for the Compute Instance is taken from the Configuration of the Function that creates the Compute Instance. If the object has it’s name ending with “_2.2” the shape will be VM.Standard2.2. The dash is important so keep in mind to put it.

   ![](./images/CreateInstanceConfig.png)

    You can change the Configuration of the function from the Console by clicking on the edit button marked with red. You can change either the subnet in which the Instances will be created, wheter or not the instances will have public_ip and edit it the corresponding shape for each key in the “shapes” map. For example “2.1” has the corresponding shape “VM.Standard2.1”.



## Prerequisites
 - An OCI bucket that has the Emit Object Events enabled

 - A subnet for the application

 - A subnet for the Compute Instances

 - Docker (It must be up and running since it will be used to build the 2 images and push them in the Repository)

 - OCI Ansible modules

   https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/ansiblegetstarted.htm

 - Docker Ansible modules
   
   https://pypi.org/project/docker/

 - OCI Authentication
   
   It uses the default ~/.oci/config file to authenticate to OCI. For more Info (https://docs.oracle.com/en-us/iaas/Content/API/Concepts/sdkconfig.htm)

 - You must have privileges to create dynamic groups and policies, since these will be created by the setup.yaml playbook and will be used by the functions.
 
   Find more about this this here (https://docs.oracle.com/en-us/iaas/Content/Functions/Tasks/functionsaccessingociresources.htm) and here (https://medium.com/oracledevs/example-of-oci-function-as-resource-principal-enabled-to-invoke-oci-services-3116fc8f6c50)



## Populating the inventory_setup.ini file
You will have to set the values for the following variables:
 - user_id – your user ocid
 - region – the region where you want to create the resources
 - compartment – the compartment where you want to create the resources
 - bucket_name – the name of the pre-existing bucket where you will upload the vmdks
 - repository_name – a name that you want to set for the repository
 - app_name – a name that you want to set for the application
 - app_subnet_id – the ocid of the subnet in which the app will reside
 - instances_subnet_id – the ocid of the subnet in which the app will reside
 - assign_pub_ip – whether or not the instances will have public ip(default is False)
 - tag_build – a tag that you want to set for the images
 - func_convert_vmdk - a name that you want to set for the function that will convert vmdk to Custom Image
 - convert_docker_image - a name that you want to set for the convert docker image
 - func_create_instance - a name that you want to set for the function that will create the Compute Instance
 - create_instance_docker_image - a name that you want to set for the create instance docker image


## Running the code

 - `ansible-playbook setup.yaml -i inventory_setup.ini -vvv`   to deploy everything
 - `ansible-playbook destroy_setup.yaml –i inventory_setup.ini -vvv`   to destroy the resources created with setup.yaml

## Known issues

- Token

In case you already have 2 token created the setup will raise an error as you can only have 2 token per user

After the token is created it's takes a few moments until will be ready to use so you might
see the play-book re-trying to connect to OCI Container registry a few times.
By default it's tryies 12 times
