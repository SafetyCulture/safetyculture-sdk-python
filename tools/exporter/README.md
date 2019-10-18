# iAuditor Data Exporter Tool

The iAuditor Data Exporter Tool is a Python script designed to make exporting data from the iAuditor API easier, faster and more efficient. This tool's primary aim is to export data into formats that work well with BI tools but it can also be used to export information in other formats.

The script is available for you to run on your local machine or server. A docker image and a docker-compose file are also available to assist in the deployment of the script. Docker is by far the easiest way to get set up, so we'd recommend using it if you're able to. 

## Initial Setup -  All users
### Regardless of how you're deploying the script, you'll need to follow these steps first.

1. Download this entire repository to a folder on your computer. If you're familiar with Git, you can clone the entire repo. If not, you can download it here.

2. Extract the zip file to your computer. It needs to be a location where ideally you won't need to move it. Your Documents folder may be a good choice. 

3. Take a look at the folder you've just extracted. You'll want to navigate to: safetyculture_sdk_python/tools/exporter/configs

3. Once in the configs folder, you'll see a file called config.yaml.sample. This file is a template for the configuration file the script uses to process your data. Open it up in a text editor (Notepad on Windows is fine)

4. You'll need to edit the config file with your details. On the left hand side of the file is the name of the config option (for example 'token' or 'template_ids') - you just need to leave a single space after the colon, then enter your required value. The table below will help with filling out the config file. For CSV Exports, all you need to give is the API key, everything else is optional. If you need help with database settings, let us know:

|  Setting | Optional? | Description  |
|---|---| --- |
| token | No | Your API key, generated from iAuditor
| config_name | Yes, unless you're using multiple configurations | You can set the name of your configuration here. Very useful if you're managing multiple as it'll be used to name files and organise folders. Do not use any spaces in this name. 
| export_path  | Yes | absolute or relative path to the directory where to save exported data to  |
| filename  |Yes |  an audit item ID whose response is going to be used to name the files of exported audit reports. Can only be an item with a response type of `text` from the header section of the audit such as Audit Title, Document No., Client / Site, Prepared By, Personnel, or any custom header item which has a 'text' type response (doesn't apply when exporting as CSV) |
| use_real_template_name | Yes | If you set this to true, the script will append the name of the template to the exported CSV file. Keep in mind that if you use this option and change the name of a template, a new file will be generated next time the script runs. |
| preferences  | Yes| to apply a preference transformation to particular templates, give here a list of preference ids
| template_ids | Yes | Here you can specify the templates from which you'd like to download your data. You need to format the templates into a list like this (including the quote marks): ```"template_123","template456","template,789"``` - If you want just one template, just write it on its own, like this: ```"template_123"```
| sync_delay_in_seconds |Yes | time in seconds to wait after completing one export run, before running again
| export_inactive_items | Yes| This setting only applies when exporting to CSV. Valid values are true (export all items) or false (do not export inactive items). Items that are nested under [Smart Field](https://support.safetyculture.com/templates/smart-fields/) will be 'inactive' if the smart field condition is not satisfied for these items.
| media_sync_offset_in_seconds | Yes | time in seconds since an audit has been modified before it will by synced
| sql_table | No if using a db | The name of the table in which you want to store your iAuditor information. Best practice is to make sure it doesn't exist, as the script will create it for you. 
| database_type | No if using a db | The type of database you're using. for SQL use 'mssql+pyodbc_mssql', for Postgres it's 'postgresql' (More should work, please refer to the SQLAlchemy documentation) 
| database_user | No if using a db | The username to login to your database
| database_pwd | No if using a db | Your database password
| database_server | No if using a db | Server where your database is located
| database_port | No if using a db | The port your database is listening on
| database_name | No if using a db | The name of the database you'll be connecting to. You can also define the driver to use if you need to - for SQL you'll likely want to add ```?driver=ODBC Driver 17 for SQL Server```

5. Once you've amended the config file. Save and close the file.
6. Right click config.yaml.sample and click 'Rename'. Remove .sample so it is called ```config.yaml```
7. That's everything for the intial set up. You can now either use Docker, or run the script directly (see below.) 

## Docker

Deployment using docker is made easy by docker compose, but you can also use the docker image directly if you like. 

To deploy directly using docker:

```
docker create \
    --name sc-exporter-tool \
    -e PUID=1000 \
    -e PGID=1000 \
    -e 'format=sql' \
    -v ./configs:/app/safetyculture-sdk-python/tools/exporter/configs \
    -v ./last_successful:/app/safetyculture-sdk-python/tools/exporter/last_successful \
    -v ./exports:/app/safetyculture-sdk-python/tools/exporter/exports \
    --restart unless-stopped \
    safetyculture/sc-exporter-tool
```

For docker-compose, move to the exporter folder then run:

```docker-compose up -d```

That's it! The docker-compose image contains some really useful additional tools:

#### Portainer
User friendly management of docker containers. We'll use this to keep an eye on the exporter.

#### CloudCMD
Easy to use, browser-based text editor. We can use this to make quick edits to the exporters config files. 

#### Metabase + Postgres
A free, open source BI tool. 

#### Adminer
A free, open source tool for inspecting databases. Useful for logging into your database and making changes. 

