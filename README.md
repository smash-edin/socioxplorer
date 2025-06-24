# SocioXplorer Project

## Description

This repository contains the code for the "Social Contextual Intelligence and Observation for Exploration of Human Behavior in Digital Environments"  (SocioXplorer) narratives analysis tool. The following figure describes the SocioXplorer system:

<p align="center">
<img width="761" alt="img_system_structure" src="https://github.com/user-attachments/assets/abb886fb-f7bb-4567-b247-f322548d46dc" />
</p>

The code for the SocioXplorer system is organised as follows:

1. [SocioXplorer Project PreProcessing Modules](/socioxplorer-backend): Raw data is ingested into the system using and then stored using the Solr indexing platform. The code for this is contained in the [`socioxplorer-backend`](/socioxplorer-backend) folder of the present repository. 
2. [SocioXplorer Dashboard](/socioxplorer-frontend): A Flask API can be used to query data from Solr and communicate it to the React UI. The code for this is contained in [`socioxplorer-frontend`](/socioxplorer-frontend) folder of the present repository. 

In this README file, we will describe how to install the SocioXplorer system and launch it. The general steps are summarised in the following figure:

<p align="center">
    <img width="761" alt="img_running_pipeline" src="https://github.com/user-attachments/assets/32d07ec5-448b-4e29-a954-00146a8bf821" />
</p>



## Table of Contents

* [1. Launching SocioXplorer for the first time](#1-launching-socioxplorer-for-the-first-time)
    * [A. Installing Prerequisite Tools and Services](#a-installing-prerequisite-tools-and-services)
    * [B. Installing `socioxplorer-backend`](#b-installing-socioxplorer-backend)
    * [C. Installing `socioxplorer-frontend`](#c-installing-socioxplorer-frontend)
* [2. Launching SocioXplorer subsequently](#2-launching-socioxplorer-subsequently)
* [3. Additional information](#3-additional-information)
* [Credits](#credits)
* [License](/LICENSE)

## 1. Launching SocioXplorer for the first time

### A. Installing Prerequisite Tools and Services

This project utilizes different tools, models and libraries. To install and start the system smoothly, please make sure to install and download the following libraries and tools:

1. ***Hardware Specifications***

    To run the system as expected, it is required to have the following hardware specifications:
    * **CPU**: A modern multi-core processor (Intel i5/i7 or AMD Ryzen 5/7) is required.
    * **RAM**: 8GB minimum (at least 16GB recommended for faster batch processing, Solr search engine, and overall system stability).
    * **Storage**: At least 4GB of free space required. These are use to store:
        * The sentence embedding model (~440MB).
        * The Solr cores that contain the data (if your dataset is very large, more space might be required).
        * Java-based network analysis models
        * Python and React dependencies (for the back-end and front-end respectively).
    * **GPU (_Optional_)**: 
        * For faster computations (e.g. for the sentence embeddings pre-processing step), a CUDA-compatible GPU (e.g., NVIDIA GTX 1050 or better) significantly improves performance. 
        * The system can also run on CPU-only, though it will be slower.

    For virtual machines, ensure that these resource allocations are met for optimal performance.


2. ***Services required***
        
    1) **Python version 3.8.19**
    
    2) **Conda 24.1.2**
    
    3) [**pip**](https://pip.pypa.io/en/stable/installation/) (Usually, pip is automatically installed if you have Python or are working in a virtual environment like conda).
    
    
    4) **Java openjdk 11.0.17**: Note that the system was tested using the Java SDK Version 11.0.25. 
    
    5) **Screen**: To test if screen is installed on your system, run the following command:
    
        ```
        screen --version
        ```
    
        This should output something similar to `Screen version 4.08.00 (GNU) 05-Feb-20`. If this does not print the expected output, install screen as follows (for Ubuntu and Debian):
    
        ```
        sudo apt update
        sudo apt install screen
        ```      
    
    8) **Node Version Manager (`nvm`)**: To check if you have `nvm`, run the following command:

       ```
       nvm --version
       ``` 

       The output should be something like `0.40.1`. If `nvm` is not installed, please refer to this webpage to install it: [https://www.freecodecamp.org/news/node-version-manager-nvm-install-guide/](https://www.freecodecamp.org/news/node-version-manager-nvm-install-guide/)
    
    10) **Apache Solr** ***9.3.0*** or ***Solr*** ***9.7.0***

    8) **Internet Access**: You will need internet access to install and launch the SocioXplorer system. You will also by default need internet access time the system ingests new data, however you can configure SocioXplorer to use a local version of the necessary models so it can function online. More information on taking the SocioXplorer system offline are given on the [`socioxplorer-backend` README.md page](/socioxplorer-backend) (see *Sentiment Analysis* and *Sentence Embeddings* sections).
    

### B. Installing `socioxplorer-backend`: 

At this point, please go to the [`socioxplorer-backend` README.md file](/socioxplorer-backend) and execute all instructions shown there. This includes following Solr installation as soon as it is mentioned in these steps, even before continuing the following steps in the socioxplorer-backend. This is vital as processes such as "importing data into solr" and "extracting data from solr" expect that the Solr instance is up and running (and that it was created successfully), and is accessible via the ***SOLR_PORT***, ***SOLR_PATH*** and ***SOLR_URL*** as configured in the system. Once this is done, come back to this page and execute the following instructions: 

1. ***Starting solr*** if it is not already running:

   1. Start a new terminal.

    2. Run the updating script:

    ```
    cd socioxplorer/socioxplorer-backend/solr
    python solr_controller.py -d start
    ```

4. ***Starting automatic updating*** if it is not already running:

    1. Start a new terminal.

    2. Run the updating script:

        * Twitter Data:

        ```
        conda activate venv
        cd socioxplorer/socioxplorer-backend/data_updater
        python3 run_scheduler.py -tc twitter_core -td path_to_twitter_data
        ```

        * YouTube Data:

        ```
        conda activate venv
        cd socioxplorer/socioxplorer-backend/data_updater
        python3 run_scheduler.py -yc youTube_core -yd path_to_youTube_data
        ```


### C. Installing `socioxplorer-frontend`


After installing the system for the first use, both the Flask API and React frontend UI should be running as explained in the [SocioXplorer Dashboard](/socioxplorer-frontend). We recommend running them in different Screen sessions or terminals (i.e. one for the Flask API and another for the React front-end) so you can monitor them.


## 2. Launching SocioXplorer subsequently

These steps are for launching the SocioXplorer system *after* it has already been installed and used at least once.

1) ***Starting solr***:

    ```
    cd socioxplorer/socioxplorer-backend/solr
    python solr_controller.py -d start
    ```

2) ***Starting flask API***:

    In a new terminal:
    
    ```
    cd socioxplorer/socioxplorer-frontend/api
    source venv/bin/activate
    cd ..
    yarn start-api
    ```

3) ***Starting UI***:

    In a new terminal:
    
    ```
    cd socioxplorer/socioxplorer-frontend/api
    source venv/bin/activate
    cd ..
    yarn start
    ```

    You may need sudo access to run these services using `sudo yarn start` and `sudo yarn start-api`.

    By following these three steps, the system is ready to be used by analysts.


## 3. Additional information

1. ***Virtual environments***

    All of the system tools depend on libraries to be installed. We use two different virtual environments to manage these libraries: 1) a conda virtual environment in the backend processing (in `socioxplorer-backend`), and 2) a python (or pip) virtual environment for the Flask API which communicates with the frontend (in `socioxplorer-frontend`). Each time a new terminal is opened, the relevant virtual environment should be activated.


## Credits:

* ### [Gephi](https://gephi.org) 
    Bastian M., Heymann S., Jacomy M. (2009). Gephi: an open source software for exploring and manipulating networks. International AAAI Conference on Weblogs and Social Media.



## 📚 Citation

If you use this work, please cite:

```bibtex
@misc{your2025arxiv,
  author       = {Sandrine Chausson and Youssef Al Hariri and Walid Magdy and Bjorn Ross},
  title        = {SocioXplorer: An Interactive Tool for Topic and Network Analysis in Social Data},
  howpublished = {\url{https://arxiv.org/abs/xxxx.xxxxx}},
  year         = {2025},
  eprint       = {xxxx.xxxxx},
  archivePrefix = {arXiv},
  primaryClass = {cs.YY}
}
