import json
from pathlib import Path

class Parameter:
    def __init__(self, param_name, param_obj):
        self.name = param_name
        self.type = param_obj.get('type')
        self.default_value = param_obj.get('defaultValue')
        self.allowed_values = param_obj.get('allowedValues')
        self.description = param_obj.get('metadata').get('description')


def generate_params(template_content):
    params = template_content['parameters']
    param_key_arr = params.keys()

    param_list = []
    for key in param_key_arr:
        param_list.append(Parameter(key, params.get(key)))
    return param_list


def generate_resource_string(template_content):
    resources = template_content['resources']
    test_resource = ''
    for r in resources:
        test_resource += r['type'] + ','
    return test_resource

def generate_template_content(file_name, paramters, template_str):
    content = f"# Provisioning Steps\n\nSee [ARM Template](https://dev.azure.com/data3-ps/TECH-Library/_git/ARM-Templates?path=%2F{file_name}) file located in the Git Repository for this Project.\n\n## Revise existing template\n\nThe template gives you most of the JSON, but you need to customise it with input Parameters to deploy it. The parameters required are contained in the parameters section of the template. These are:\n\n"

    for param in paramters:
        param_str = f"* **{param.name}:** Must be a {param.type} defining {param.description} "
        if param.default_value is not None or param.allowed_values is not None:
            if param.default_value is not None:
                if param.type == "string":
                    default_value_str = f"The default value is:\n\n\t``` json\n\t\"{param.default_value}\"\n\t```\n\n"
                else:
                    default_value_str = f"The default value is:\n\n\t``` json\n\t{param.default_value}\n\t```\n\n"
                param_str = param_str + default_value_str
            if param.allowed_values is not None:
                str = json.dumps(param.allowed_values, sort_keys=True, indent=4)
                str = '\t'.join(('\n' + str.lstrip()).splitlines(True))
                allowed_values_str = f"\tThe allowed values are:\n\n\t``` json{str}\n\t```\n\n"
                param_str = param_str + allowed_values_str
        else:
            param_str += "\n\n"
        content += param_str
    content += "These parameters are used throughout the ARM Template to inject the value(s) they contain. They are referenced using the Parameters function with the name of the Parameter. In the example below, the value for **location** using the value assigned to the **location** parameter at deployment e.g. \"Australia East\"\n\n" + "``` json\n\"location\": \"[parameters('location')]\"\n```\n\n"
    content += "The full ARM template with parameters is:\n\n``` json\n" + template_str + "\n```\n\n"
    content += "## Deploy template\n\nThe code below shows how to deploy a template via PowerShell using a Parameter Object.\n\n``` powershell\n$params = @{\n    $vmName = \"d3-linux-vm\"\n}\n\nNew-AzResourceGroupDeployment `\n    -ResourceGroupName \"ResourceGroupName\" `\n    -TemplateFile \"" + file_name + "/azuredeploy.json\" `\n    @params\n```\n\nThe code below shows how to deploy a template via PowerShell using a Parameter File.\n\n``` powershell\nNew-AzResourceGroupDeployment `\n    -ResourceGroupName \"ResourceGroupName\" `\n    -TemplateFile \""+ file_name + "/azuredeploy.json\" `\n    -TemplateParameterFile \"" + file_name + "/parameters/parameters-stg.json\"\n```"
    return content


def generate_readme_content(resource_name, paramters):
    content = f"# {resource_name}\n\n<resource_overview>\n\nThis Template builds and configures the following:\n\n\t* TBA\n\n## Parameters\n\n"

    for param in paramters:
        param_str = f"* {param.name}\n\t* {param.description}\n"
        if param.default_value is not None or param.allowed_values is not None:
            if param.default_value is not None:
                if param.type == "string":
                    default_value_str = f"\t* Default value is:\n\n\t\t``` json\n\t\t\"{param.default_value}\"\n\t\t```\n\n"
                else:
                    default_value_str = f"\t* Default value is:\n\n\t\t``` json\n\t\t{param.default_value}\n\t\t```\n\n"
                param_str = param_str + default_value_str
            if param.allowed_values is not None:
                str = json.dumps(param.allowed_values, sort_keys=True, indent=4)
                str = '\t\t'.join(('\n' + str.lstrip()).splitlines(True))
                allowed_values_str = f"\t\tThe allowed values are:\n\n\t\t``` json{str}\n\t\t```\n\n"
                param_str = param_str + allowed_values_str
        else:
            param_str += "\n"
        content += param_str

    content += "## Prerequisites\n\nAccess to Azure\n\n" \
                + "## Versioning\n\n We use [Azure DevOps](http://dev.azure.com/) for version control.\n\n" \
                + f"## Authors\n\n**Stephen Ge (Data#3)** - *Initial work* - [{resource_name}](https://dev.azure.com/data3-ps/TECH-Library/_git/ARM-Templates?path=%2F{'-'.join(resource_name.split())})\n\n" \
                + "See also the list of [contributors](https://dev.azure.com/data3-ps/TECH-Library/_git/ARM-Templates/commits) who participated in this project.\n\n"
    return content


def write_to_file(file_path, content):
    file = open(file_path, "w+")
    file.write(content)


def main():
    resource_name = "Azure VPN"
    file_name = '-'.join(resource_name.split())
    dir_arm_template = "/Users/stephenge/Documents/dev/AzureMSPServices/ARM-Templates"
    dir_output = "/Users/stephenge/Documents/dev/DocAutoGen"

    with open(f'{dir_arm_template}/{file_name}/azuredeploy.json') as f:
        data = json.load(f)

    param_list = generate_params(data)
    test_parameters = ''
    for p in param_list:
        test_parameters += p.name + ','
    print(test_parameters)
    print()
    test_resources = generate_resource_string(data)
    print(test_resources)

    arm_template_content = generate_template_content(file_name, param_list, json.dumps(data, indent=4, sort_keys=True))
    # print(arm_template_content)
    readme_content = generate_readme_content(resource_name, param_list)
    # print(readme_content)

    dir_service = f"{dir_output}/Outputs/{file_name}"
    dir_provision = f"{dir_output}/Outputs/{file_name}/Provisioning-Guidance"
    Path(dir_provision).mkdir(parents=True, exist_ok=True)

    # Order
    content_provision_order = "User-Interface-(UI)\nCLI-Script\nARM-Template\nTesting-Steps"
    write_to_file(f"{dir_provision}/.order", content_provision_order)

    # CLI-Script
    content_provision_cli = "# Provisioning Steps\n\n" \
                            "## Prerequisites\n\n* An Azure subscription.\n* Install the latest Azure PowerShell modules by following instructions in [How to install and configure Azure PowerShell](https://docs.microsoft.com/en-us/powershell/azure/install-Az-ps?view=azps-3.4.0).\n\n## Log in to PowerShell\n\n1. Launch PowerShell on your machine.\n2. Run the following command, and enter the same Azure username and password that you use to sign in to the Azure portal:\n\n   ``` powershell\n   # Sign in Azure Account\n   Connect-AzAccount\n   ```"
    write_to_file(f"{dir_provision}/CLI-Script.md", content_provision_cli)

    # Testing-Steps
    content_provision_test = "# Testing\n\n" \
                             "To validate the deployment, you can either use the Azure portal to check the " + resource_name + " or use the following PowerShell script.\n\n" \
                                                                                                                               "## UI\n\n1. In the top search field, type virtual machines.\n2. Select Virtual Machines.\n3. Look through the list of the virtual machines found. You can filter based on subscription, resource groups, location and etc.\n\n   ![image.png](/.attachments/image-a3f60dbb-f842-4103-9c62-f71315f6c4c2.png)\n\n4. Select a virtual machine to display its properties.\n\n   ![image.png](/.attachments/image-134ab366-b185-4882-a36e-6ef056dc23b5.png)\n\n# Powershell\n``` powershell\nGet-AzVM -ResourceGroupName $resourceGroupName -Name $vmName\n```\nIf the service is deployed successfully, you see output similar to the following sample:\n### Powershell\n``` powershell\nResourceGroupName  : Individual_Stephen-Ge\nId                 :\n/subscriptions/73515f85-5a1f-4d98-a1ae-64f54c962d88/resourceGroups/Individual_Stephen-Ge/providers/Microsoft.Compute/virtualMachines/testVM\nVmId               : 1df9018e-7ca9-4ca2-87d0-c578e951dd72\nName               : testVM\nType               : Microsoft.Compute/virtualMachines\nLocation           : australiaeast\nTags               : {}\nDiagnosticsProfile : {BootDiagnostics}\nHardwareProfile    : {VmSize}\nNetworkProfile     : {NetworkInterfaces}\nOSProfile          : {ComputerName, AdminUsername, LinuxConfiguration, Secrets, AllowExtensionOperations, RequireGuestProvisionSignal}\nProvisioningState  : Succeeded\nStorageProfile     : {ImageReference, OsDisk, DataDisks}\n```"
    write_to_file(f"{dir_provision}/Testing-Steps.md", content_provision_test)

    # User-Interface-(UI).md
    content_provision_ui = "# Provisioning Steps\n\n## Prerequisites\n\nAn Azure subscription\n"
    write_to_file(f"{dir_provision}/User-Interface-(UI).md", content_provision_ui)
    write_to_file(f"{dir_provision}/ARM-Template.md", arm_template_content)

    write_to_file(f"{dir_service}/README.md", readme_content)

    # print(json.dumps(parameter_str, indent = 4, sort_keys=True))


if __name__ == '__main__':
    main()
