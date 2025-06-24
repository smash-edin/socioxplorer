# PreProcessing - Apache Solr Instance Controller Module

## Description

This folder contains a simple controller to control the Apache Solr Platform for the usage in the SocioXplorer analysis tool from the project SocioXplorer.

## Download the project repo:

Please make sure that you downloaded the socioxplorer repository.

## Downloading Apache Solr:

Download the Solr from [Solr Apache](https://solr.apache.org/downloads.html).

The system is intensively tested with [Solr 9.3.0](https://archive.apache.org/dist/solr/solr/9.3.0/solr-9.3.0.tgz). Also, we tested the system with [Solr 9.7.0](https://archive.apache.org/dist/solr/solr/9.7.0/solr-9.7.0.tgz). 
Both are working fine, but we highly recommend using 9.3.0.

## Installing Solr

After downloading Solr, decompress the file in a folder of your choice. It is not mandatory to have the solr folder within the
`socioxplorer` folder. However, the system is prepared to have Solr stored in the same location where it is located. In other words, for hassle-free installation, make the three folders (`socioxplorer` and `solr-9.3.0`) have the same parent folder.

After that please follow the following steps carefully:

1. Update the file ***./solr_path/bin/solr.in.sh*** for server running with **Linux/Max OS**, (**_or_**
   ***./solr_path/bin/solr.in.cmd*** for servers with **Microsoft OS**) with the following settings:
    1. For a scalable usage of Solr:
        1. comment the line that has the value SOLR_HEAP. It should be as following:
       ```
       #SOLR_HEAP=
       ```
        2. Uncomment the line with the constant SOLR_JAVA_MEM and set it with the following parameters in case the data
           is extremely large make it as follow:
       ```
       SOLR_JAVA_MEM="-Xms10g -Xmx20g"
       ```

       however, if the resources in you machine, or you are using a virtual machine, then you need to consider the limitations here. For instance, if your machine is up to 8GB of RAM, then, the default value would be fine, or, you may set it to `SOLR_JAVA_MEM="-Xms512m -Xmx2g"` 

    2. Uncomment and set the line with SOLR_PORT assignment to the desired port number. For example, in the default configurations we use the port 10196 as shown below:
   ```
   SOLR_PORT=10196
   ```
    3. (If security is a concern and the url is publicly accessible), add the url of Solr host to the SOLR_IP_ALLOWLIST as follow:
   ```
   SOLR_IP_ALLOWLIST=127.0.0.1,<server.co.uk>
   ```
   However, the server address here (server.co.uk) is just a sample name, and it should be replaced by your own server address or removed and keep the localhost (127.0.0.1) or replace it with the IP address that the system will access Solr from. Multiple addresses/IPs can be added, separated by commas (,).
   
   This step may prevent you from accessing Solr, so please make sure to add the correct ip(s).

    4. Set SOLR_JETTY_HOST setting. For security, you may consider running the Solr of the same server that runs other
       modules and keep the SOLR_JETTY_HOST=127.0.0.1. If security is not concern, then you may consider making SOLR_JETTY_HOST=0.0.0.0. Below is a sample of settings to have Jetty host to 0.0.0.0
       ```
       SOLR_JETTY_HOST=0.0.0.0
       ```
    5. Save the **_solr.in.sh_** (or **_solr.in.cmd_** in MS Windows) file.



2. Update the ***_configs.py_*** file in the root folder of the repo with the port number you specified in the ApplicationConfig class. Make sure that the attributes ***SOLR_PORT***, ***SOLR_PATH*** and ***SOLR_URL*** hold the correct values. For the path, it should be the relative path from inside the folder `solr` that is inside the `socioxplorer-backend` folder. In other words, the ***SOLR_PATH*** should be set relative to the folder that includes `solr_controller.py` file.

3. If you did not generate the required environment variables, please run the following command from the ***root*** folder of the repository:

   ```
   python generate_codes.py
   ```

## Running Solr

  * To *start* Solr, from the solr folder, that is `socioxplorer/socioxplorer-backend/solr`, run the following command:
   ```
   python solr_controller.py -d start
   ```

   If the error message "Port is already being used" printed, then check if another service uses the port number you
   identified above, or if Solr is already running with this Port. 
   
   ***NOTE 1:*** Solr *must be running* for the SocioXplorer system to work, whether that's for pre-processing steps or for running the UI.

   * In case you need to *restart* the Solr, you can do this with this command:
   ```
   python solr_controller.py -d restart
   ```

   * To *stop* the Solr, run the following command:
   ```
   python solr_controller.py -d stop
   ```

   Remember that if you stop the Solr, the system won't be able to function anymore. You would need to start the Solr again to make it functional.
   
## Creating a new Solr core

To create a new collection (aka core), with the name new_core, please run the following command:

   ```
   python solr_controller.py -d add -c new_core
   ```
   The expected result is: Created new core 'new_core'. In case the core is already exists, the error
   message "Core 'new_core' already exists!" will be shown. In this case, you need to check the available cores.

   After creating the core successfully, please check that the list ***SOLR_CORES*** in the ApplicationConfig class (in the configs.py file that is located in the root of this repo) so it includes the name of the new created core and if not please add the core's name to the list. Also, check that the ***datasetOptions.csv*** file inside the folder `socioxplorer/socioxplorer-frontend/src/.data/` contains the newly created core, if not please add key, value and text to the file as comma separated as shown below:
   ```
   "NewCore","New Core","new_core"
   ```
   
   NOTE: Please notice that if you are using a spreadsheet editor, such as Excel, you do not need to add the quotation char ("), as this will change the name of the core and will affect the system. The double quotation is shown in our example as we are using text editors.


   Below you can see a sample of the datasetOptions.csv contents after adding two cores (new_core_y and new_core):
   ```
   key,text,value
   "YouTubeCore","YouTubeCore","new_core_y"
   "NewCore","New Core","new_core"
   ```

   And below you can see it in a ***Spreadsheet*** application:
   
   
   |   **key**   | **text**  | **value**|
   |:-----------:|:---------:|:--------:|
   | YouTubeCore |YouTubeCore|new_core_y|
   |  NewCore    |  New Core | new_core |



   As you may notice, the ***value*** is expected to be identical to the generated core name (new_core in this example), the ***key*** and ***text*** can be different. The text will be used to show the core's name in the web interface, so please make sure that it is informative and readable. Please make sure that the header of this file is kept as it is "key,text,value".


   Note: although deleting the core and starting Solr might be performed directly through Solr interface, creating the core should be done by this tool to initiate the required fields in the schema file. Otherwise, the system might not work as expected.

## Deleting Solr cores

To delete the already exist core named new_core **(** ***CAUTION***: this process is non-reversible and will remove the core
   permanently **)**, run the following command:
   ```
   python solr_controller.py -d delete -c new_core
   ```

   The expected message is "The collection has been deleted successfully. However, if the core does not exist or the port/path settings have inaccurate details you may get the
   error message: "Cannot unload non-existent core".

   Moreover, after deleting the core successfully, please check that the list ***SOLR_CORES*** in the ApplicationConfig class (inside configs.py file within the root folder of this repo) so it does not include the name of the delete core and if it exists, please remove it from the list. Also, please check that the ***datasetOptions.csv*** file inside the `socioxplorer/socioxplorer-frontend/src/.data/` folder does not contain the deleted core, if not please delete the line with the key, value and text relevant to the deleted core. The sample mentioned above of two cores should become as follow after deleting the core "new_core":

   ```
   key,text,value
   "YouTubeCore","YouTubeCore","new_core_y"
   ```
   
   NOTE: After deleting all records, the content of the file ***datasetOptions.csv***  should be as follow:

   ```
   key,text,value
   ```
   
   This finishes the instructions to install and handle Solr instance in your system.
