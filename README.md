# DocAutoGen

This is a simple python script to generate part of wiki required for each MSP service.

## Get started
1. Open `WikiGenerator.py` file.
2. Find `main()` function.
    1. Change the value of `resource_name` to the service name to be created, for example `"Azure VPN"`.
    2. Change the value of `dir_arm_template` to the directory where your arm template is located on your machine locally, for example: 
        ```
        "/Users/stephenge/Documents/dev/AzureMSPServices/ARM-Templates"
        ```
    3. Change the value of `dir_output` to the directory where this script is located as output directory, for example: 
        ```
        "/Users/stephenge/Documents/dev/DocAutoGen"
        ```
3. Save changes and run this script, you should see a folder named "output" is created in the output directory specified above with a service folder in it.
4. You should also see two strings are generated in the console output. They are `TEST_parameters` and `TEST_resources` for Variable Groups in DevOps, for example:
    ```
    projectName,location,sku,vpnType,vnetAddressPrefix,subnetPrefix,partner_reg_guid,
    
    Microsoft.Resources/deployments,Microsoft.Network/virtualNetworkGateways,Microsoft.Network/publicIPAddresses,Microsoft.Network/virtualNetworks,
    ```