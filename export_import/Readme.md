# Exporting vmdk from VMware and import them in the bucket Automation

## Introduction

The export_import.yaml Ansible playbook will take care of exporting the vmdks from VMware and importing them in an OCI Bucket.

Both export and import are done in parallel using async and poll, so it will be a lot quicker than doing it one by one.

### In this folder you will find:

 - export_import.yaml – Ansible playbook that takes care of export from VMware and Import into OCI Bucket

 - setup.iss – Response file used to install the WinVirtIO agent on Windows Machines

 - Readme.md - Readme file


## Workflow

 - First the code will gather informations about the VMs and will create 3 lists:

     - vm_list - List of all VMs
     - windows_vm_list - List containing only the Windows VMs
     - linux_vm_list - List containing only the Linux VMs

 - Then, based on the variable RunWinTasks, there are 2 scenarios

     - If you set RunWinTasks to true, it will run the Windows related block of code, which will check if the WinVirtIO agent is installed on the Windows Machines, if not it will copy and install it using the response file, it will shut down all VMs( Both Windows and Linux) to be able to export them and after the export it will power them on.
    
     - If you set RunWinTasks to false, then the code will go to the Linux block of code, where it will power off only the Linux VMs, export them and power them on.
 
 
 - After either of the blocks have finished, it will get the vmdk files path(example: v_path/2.2/testlinux/testlinux.vmdk), upload the vmdks and will set the objects name based on the folder that they were in (example: testlinux_2.2).



###   In both scenarios, the export is done the same way. It will check the hw specifications of each vm and will export them in a designated folder inside the v_path variable.

`export_dir: "{% if item.instance.hw_memtotal_mb <= 15360 and item.instance.hw_processor_count < 2 %}./{{ v_path }}/2.1{% elif item.instance.hw_memtotal_mb <= 30720 and item.instance.hw_processor_count < 3 %}./{{ v_path }}/2.2{% elif item.instance.hw_memtotal_mb <= 61440 and item.instance.hw_processor_count <= 4 %}./{{ v_path }}/2.4{% elif item.instance.hw_memtotal_mb <= 122880 and item.instance.hw_processor_count <= 8 %}./{{ v_path }}/2.8{% elif item.instance.hw_memtotal_mb <= 245760 and item.instance.hw_processor_count <= 16 %}./{{ v_path }}/2.16{% elif item.instance.hw_memtotal_mb > 245760 and item.instance.hw_processor_count > 16 %}./{{ v_path }}/2.24{% endif %}"`

 - This will cover all shapes for VM.Standard2.

 - So if a VM with the name “Vmtest” has the memory between 15 and 30 GB and less than 3 cpus, will be exported in “v_path/2.2/VMtest/Vmtest.vmdk”.

## Prerequisites:
 - OCI Ansible modules

     https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/ansiblegetstarted.htm

 - VMware Ansible modules

     https://docs.ansible.com/ansible/latest/scenario_guides/vmware_scenarios/vmware_intro.html

 - Windows Ansible modules

     `ansible-galaxy collection install ansible.windows`

 - Winrm installed on the Windows virtual machines 

 - Oracle VirtIO Drivers
    If you want to export and create Instances from Windows machines too, these drivers need to be installed on them.
    The script will take care of the installation using the response file, but the zip file containing needs to be downloaded and put in the export_import folder where the response file is.
    [This link](https://objectstorage.eu-frankfurt-1.oraclecloud.com/p/UZ7AnzjdtVMWWqdzFn8w_z6DYKPWyxXKQtMZ8CumJ_6g[…]enatdpltintegration03/b/buck1/o/V984560-01.zip) contains a PAR to download the ZIP file for Oracle VirtIO Drivers 1.1.5.
    If you want another version or the PAR is not working, you can download it from [Oracle delivery site](https://edelivery.oracle.com/osdc/faces/SoftwareDelivery).
    
    Steps:

         - Go to the delivery site
         - search for "Oracle Linux"
         - select a version (to get 1.1.5 select Oracle Linux 7.7.0.0.0)
         - in the checkout select Platform x86 64 bit
         - accept terms
         - select Oracle VirtIO Drivers Version for Microsoft Windows 1.1.5 from that list to download it
         - move it in the export_import folder (where the response file is)



The Windows Ansible modules, Winrm and Oracle VirtIO drivers are only required if you set RunWinTasks to true.


## Populating the variables
The variables needed by the workflow are found inside the playbook:

 - v_bucket_name – the name of a pre-existing bucket where you will upload the vmdks
 - v_namespace – the object storage namespace ( To view your object storage namespace, open the profile menu in the console , click on Tenancy and it should be listed under Object Storage Settings.
 - v_path – the path where the vmdks will be exported
 - v_pattern: "*.vmdk" – don’t edit this one. It is used by the workflow to look only for vmdk files
 - hostname – Vmware hostname
 - username – Vmware password
 - datacenter – Vmware datacenter
 - RunWinTasks – Whether or not to run the code block that will install the VirtIO agent and export all VMs. If this is set to false, only the Linux VMs will be exported
 - ansible_winrm_pass – password for the Windows machines
 - ansible_winrm_user – username for the Windows machines

## Running the code:

 - `ansible-playbook export_import.yaml -vvv` 