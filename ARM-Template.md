# Provisioning Steps

See [ARM Template](https://dev.azure.com/data3-ps/TECH-Library/_git/ARM-Templates?path=%2FAzure-Virtual-Machine-Scale-Sets) file located in the Git Repository for this Project.

## Revise existing template

The template gives you most of the JSON, but you need to customise it with input Parameters to deploy it. The parameters required are contained in the parameters section of the template. These are:

* **vmSku:** Must be a string defining Size of VMs in the VM Scale Set. The default value is:

	``` json
	"Standard_D1_v2"
	```

* **vmssName:** Must be a string defining String used as a base for naming resources (9 characters or less). A hash is prepended to this string for some resources, and resource-specific information is appended. 

* **instanceCount:** Must be a int defining Number of VM instances (100 or less). The default value is:

	``` json
	1
	```

* **adminUsername:** Must be a string defining Admin username on all VMs. 

* **authenticationType:** Must be a string defining Type of authentication to use on the Virtual Machine. SSH key is recommended. The default value is:

	``` json
	"password"
	```

	The allowed values are:

	``` json
	[
	    "sshPublicKey",
	    "password"
	]
	```

* **adminPasswordOrKey:** Must be a securestring defining SSH Key or password for the Virtual Machine. SSH key is recommended. 

* **location:** Must be a string defining The location in which the Event Grid resources should be deployed. The default value is:

	``` json
	"[resourceGroup().location]"
	```

* **partner_reg_guid:** Must be a string defining Azure Partner Registration GUID The default value is:

	``` json
	"68018b1d-e958-5810-ad55-75e681beb6ce"
	```

	The allowed values are:

	``` json
	[
	    "68018b1d-e958-5810-ad55-75e681beb6ce"
	]
	```

These parameters are used throughout the ARM Template to inject the value(s) they contain. They are referenced using the Parameters function with the name of the Parameter. In the example below, the value for **location** using the value assigned to the **location** parameter at deployment e.g. "Australia East"

``` json
"location": "[parameters('location')]"
```

The full ARM template with parameters is:

``` json
{
    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "functions": [],
    "outputs": {},
    "parameters": {
        "adminPasswordOrKey": {
            "metadata": {
                "description": "SSH Key or password for the Virtual Machine. SSH key is recommended."
            },
            "type": "securestring"
        },
        "adminUsername": {
            "metadata": {
                "description": "Admin username on all VMs."
            },
            "type": "string"
        },
        "authenticationType": {
            "allowedValues": [
                "sshPublicKey",
                "password"
            ],
            "defaultValue": "password",
            "metadata": {
                "description": "Type of authentication to use on the Virtual Machine. SSH key is recommended."
            },
            "type": "string"
        },
        "instanceCount": {
            "defaultValue": 1,
            "maxValue": 100,
            "metadata": {
                "description": "Number of VM instances (100 or less)."
            },
            "type": "int"
        },
        "location": {
            "defaultValue": "[resourceGroup().location]",
            "metadata": {
                "description": "The location in which the Event Grid resources should be deployed."
            },
            "type": "string"
        },
        "partner_reg_guid": {
            "allowedValues": [
                "68018b1d-e958-5810-ad55-75e681beb6ce"
            ],
            "defaultValue": "68018b1d-e958-5810-ad55-75e681beb6ce",
            "metadata": {
                "description": "Azure Partner Registration GUID"
            },
            "type": "string"
        },
        "vmSku": {
            "defaultValue": "Standard_D1_v2",
            "metadata": {
                "description": "Size of VMs in the VM Scale Set."
            },
            "type": "string"
        },
        "vmssName": {
            "maxLength": 9,
            "metadata": {
                "description": "String used as a base for naming resources (9 characters or less). A hash is prepended to this string for some resources, and resource-specific information is appended."
            },
            "type": "string"
        }
    },
    "resources": [
        {
            "apiVersion": "2018-02-01",
            "name": "[concat('pid-', parameters('partner_reg_guid'))]",
            "properties": {
                "mode": "Incremental",
                "template": {
                    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
                    "contentVersion": "1.0.0.0",
                    "resources": []
                }
            },
            "type": "Microsoft.Resources/deployments"
        },
        {
            "apiVersion": "2017-04-01",
            "location": "[parameters('location')]",
            "name": "[variables('virtualNetworkName')]",
            "properties": {
                "addressSpace": {
                    "addressPrefixes": [
                        "[variables('addressPrefix')]"
                    ]
                },
                "subnets": [
                    {
                        "name": "[variables('subnetName')]",
                        "properties": {
                            "addressPrefix": "[variables('subnetPrefix')]"
                        }
                    }
                ]
            },
            "type": "Microsoft.Network/virtualNetworks"
        },
        {
            "apiVersion": "2017-04-01",
            "location": "[parameters('location')]",
            "name": "[variables('publicIPAddressName')]",
            "properties": {
                "dnsSettings": {
                    "domainNameLabel": "[parameters('vmssName')]"
                },
                "publicIPAllocationMethod": "Dynamic"
            },
            "type": "Microsoft.Network/publicIPAddresses"
        },
        {
            "apiVersion": "2017-04-01",
            "dependsOn": [
                "[concat('Microsoft.Network/publicIPAddresses/', variables('publicIPAddressName'))]"
            ],
            "location": "[parameters('location')]",
            "name": "[variables('loadBalancerName')]",
            "properties": {
                "backendAddressPools": [
                    {
                        "name": "[variables('bePoolName')]"
                    }
                ],
                "frontendIPConfigurations": [
                    {
                        "name": "LoadBalancerFrontEnd",
                        "properties": {
                            "publicIPAddress": {
                                "id": "[variables('publicIPAddressID')]"
                            }
                        }
                    }
                ],
                "inboundNatPools": [
                    {
                        "name": "[variables('natPoolName')]",
                        "properties": {
                            "backendPort": "[variables('natBackendPort')]",
                            "frontendIPConfiguration": {
                                "id": "[variables('frontEndIPConfigID')]"
                            },
                            "frontendPortRangeEnd": "[variables('natEndPort')]",
                            "frontendPortRangeStart": "[variables('natStartPort')]",
                            "protocol": "Tcp"
                        }
                    },
                    {
                        "name": "natpool2",
                        "properties": {
                            "backendPort": "9000",
                            "frontendIPConfiguration": {
                                "id": "[variables('frontEndIPConfigID')]"
                            },
                            "frontendPortRangeEnd": "9120",
                            "frontendPortRangeStart": "9000",
                            "protocol": "Tcp"
                        }
                    }
                ]
            },
            "type": "Microsoft.Network/loadBalancers"
        },
        {
            "apiVersion": "2017-03-30",
            "dependsOn": [
                "[concat('Microsoft.Network/loadBalancers/', variables('loadBalancerName'))]",
                "[concat('Microsoft.Network/virtualNetworks/', variables('virtualNetworkName'))]"
            ],
            "location": "[parameters('location')]",
            "name": "[parameters('vmssName')]",
            "properties": {
                "overprovision": "false",
                "upgradePolicy": {
                    "mode": "Manual"
                },
                "virtualMachineProfile": {
                    "extensionProfile": {
                        "extensions": [
                            {
                                "name": "lapextension",
                                "properties": {
                                    "autoUpgradeMinorVersion": true,
                                    "publisher": "Microsoft.Azure.Extensions",
                                    "settings": {
                                        "commandToExecute": "bash installserver.sh",
                                        "fileUris": [
                                            "https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/201-vmss-bottle-autoscale/installserver.sh",
                                            "https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/201-vmss-bottle-autoscale/workserver.py"
                                        ]
                                    },
                                    "type": "CustomScript",
                                    "typeHandlerVersion": "2.0"
                                }
                            }
                        ]
                    },
                    "networkProfile": {
                        "networkInterfaceConfigurations": [
                            {
                                "name": "[variables('nicName')]",
                                "properties": {
                                    "ipConfigurations": [
                                        {
                                            "name": "[variables('ipConfigName')]",
                                            "properties": {
                                                "loadBalancerBackendAddressPools": [
                                                    {
                                                        "id": "[concat('/subscriptions/', subscription().subscriptionId,'/resourceGroups/', resourceGroup().name, '/providers/Microsoft.Network/loadBalancers/', variables('loadBalancerName'), '/backendAddressPools/', variables('bePoolName'))]"
                                                    }
                                                ],
                                                "loadBalancerInboundNatPools": [
                                                    {
                                                        "id": "[concat('/subscriptions/', subscription().subscriptionId,'/resourceGroups/', resourceGroup().name, '/providers/Microsoft.Network/loadBalancers/', variables('loadBalancerName'), '/inboundNatPools/', variables('natPoolName'))]"
                                                    },
                                                    {
                                                        "id": "[concat('/subscriptions/', subscription().subscriptionId,'/resourceGroups/', resourceGroup().name, '/providers/Microsoft.Network/loadBalancers/', variables('loadBalancerName'), '/inboundNatPools/natpool2')]"
                                                    }
                                                ],
                                                "subnet": {
                                                    "id": "[concat('/subscriptions/', subscription().subscriptionId,'/resourceGroups/', resourceGroup().name, '/providers/Microsoft.Network/virtualNetworks/', variables('virtualNetworkName'), '/subnets/', variables('subnetName'))]"
                                                }
                                            }
                                        }
                                    ],
                                    "primary": true
                                }
                            }
                        ]
                    },
                    "osProfile": {
                        "adminPassword": "[parameters('adminPasswordOrKey')]",
                        "adminUsername": "[parameters('adminUsername')]",
                        "computerNamePrefix": "[parameters('vmssName')]",
                        "linuxConfiguration": "[if(equals(parameters('authenticationType'), 'password'), json('null'), variables('linuxConfiguration'))]"
                    },
                    "storageProfile": {
                        "imageReference": "[variables('imageReference')]",
                        "osDisk": {
                            "caching": "ReadWrite",
                            "createOption": "FromImage"
                        }
                    }
                }
            },
            "sku": {
                "capacity": "[parameters('instanceCount')]",
                "name": "[parameters('vmSku')]",
                "tier": "Standard"
            },
            "type": "Microsoft.Compute/virtualMachineScaleSets"
        },
        {
            "apiVersion": "2015-04-01",
            "dependsOn": [
                "[concat('Microsoft.Compute/virtualMachineScaleSets/', parameters('vmSSName'))]"
            ],
            "location": "[parameters('location')]",
            "name": "autoscalehost",
            "properties": {
                "enabled": true,
                "name": "autoscalehost",
                "profiles": [
                    {
                        "capacity": {
                            "default": "1",
                            "maximum": "10",
                            "minimum": "1"
                        },
                        "name": "Profile1",
                        "rules": [
                            {
                                "metricTrigger": {
                                    "metricName": "Percentage CPU",
                                    "metricNamespace": "",
                                    "metricResourceUri": "[concat('/subscriptions/',subscription().subscriptionId, '/resourceGroups/',  resourceGroup().name, '/providers/Microsoft.Compute/virtualMachineScaleSets/', parameters('vmSSName'))]",
                                    "operator": "GreaterThan",
                                    "statistic": "Average",
                                    "threshold": 60,
                                    "timeAggregation": "Average",
                                    "timeGrain": "PT1M",
                                    "timeWindow": "PT5M"
                                },
                                "scaleAction": {
                                    "cooldown": "PT1M",
                                    "direction": "Increase",
                                    "type": "ChangeCount",
                                    "value": "1"
                                }
                            },
                            {
                                "metricTrigger": {
                                    "metricName": "Percentage CPU",
                                    "metricNamespace": "",
                                    "metricResourceUri": "[concat('/subscriptions/',subscription().subscriptionId, '/resourceGroups/',  resourceGroup().name, '/providers/Microsoft.Compute/virtualMachineScaleSets/', parameters('vmSSName'))]",
                                    "operator": "LessThan",
                                    "statistic": "Average",
                                    "threshold": 30,
                                    "timeAggregation": "Average",
                                    "timeGrain": "PT1M",
                                    "timeWindow": "PT5M"
                                },
                                "scaleAction": {
                                    "cooldown": "PT1M",
                                    "direction": "Decrease",
                                    "type": "ChangeCount",
                                    "value": "1"
                                }
                            }
                        ]
                    }
                ],
                "targetResourceUri": "[concat('/subscriptions/',subscription().subscriptionId, '/resourceGroups/',  resourceGroup().name, '/providers/Microsoft.Compute/virtualMachineScaleSets/', parameters('vmSSName'))]"
            },
            "type": "Microsoft.Insights/autoscaleSettings"
        }
    ],
    "variables": {
        "addressPrefix": "10.0.0.0/16",
        "bePoolName": "[concat(parameters('vmssName'), '-bepool')]",
        "frontEndIPConfigID": "[concat(variables('lbID'),'/frontendIPConfigurations/loadBalancerFrontEnd')]",
        "imageReference": "[variables('osType')]",
        "ipConfigName": "[concat(parameters('vmssName'), '-ipconfig')]",
        "lbID": "[resourceId('Microsoft.Network/loadBalancers',variables('loadBalancerName'))]",
        "linuxConfiguration": {
            "disablePasswordAuthentication": true,
            "ssh": {
                "publicKeys": [
                    {
                        "keyData": "[parameters('adminPasswordOrKey')]",
                        "path": "[concat('/home/', parameters('adminUsername'), '/.ssh/authorized_keys')]"
                    }
                ]
            }
        },
        "loadBalancerName": "[concat(parameters('vmssName'), '-lb')]",
        "natBackendPort": 22,
        "natEndPort": 50120,
        "natPoolName": "[concat(parameters('vmssName'), '-natpool')]",
        "natStartPort": 50000,
        "nicName": "[concat(parameters('vmssName'), '-nic')]",
        "osType": {
            "offer": "UbuntuServer",
            "publisher": "Canonical",
            "sku": "16.04-LTS",
            "version": "latest"
        },
        "publicIPAddressID": "[resourceId('Microsoft.Network/publicIPAddresses',variables('publicIPAddressName'))]",
        "publicIPAddressName": "[concat(parameters('vmssName'), '-pip')]",
        "subnetName": "[concat(parameters('vmssName'), '-subnet')]",
        "subnetPrefix": "10.0.0.0/24",
        "virtualNetworkName": "[concat(parameters('vmssName'), '-vnet')]"
    }
}
```

## Deploy template

The code below shows how to deploy a template via PowerShell using a Parameter Object.

``` powershell
$params = @{
    $vmName = "d3-linux-vm"
}

New-AzResourceGroupDeployment `
    -ResourceGroupName "ResourceGroupName" `
    -TemplateFile "Azure-Virtual-Machine-Scale-Sets/azuredeploy.json" `
    @params
```

The code below shows how to deploy a template via PowerShell using a Parameter File.

``` powershell
New-AzResourceGroupDeployment `
    -ResourceGroupName "ResourceGroupName" `
    -TemplateFile "Azure-Virtual-Machine-Scale-Sets/azuredeploy.json" `
    -TemplateParameterFile "Azure-Virtual-Machine-Scale-Sets/parameters/parameters-stg.json"
```