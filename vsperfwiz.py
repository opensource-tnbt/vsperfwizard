from __future__ import print_function
from pypsi import wizard as wiz
from pypsi.shell import Shell
import nicinfo

def main():
    shell = Shell()
    dev_list = nicinfo.get_nic_details()
    devices = ''
    for dev in dev_list:
        devices += str(dev["Interface"]) + '::' + str(dev["Slot"]) + ', '
    print(devices)
    wiz_main = wiz.PromptWizard(
        name="VSPERF Common Configuration",
        description="This configuration covers Basic inputs",
        steps=(
            # The list of input prompts to ask the user.
            wiz.WizardStep(
                # ID where the value will be stored
                id="vswitch",
                # Display name
                name="Vswitch ? [OVS or VPP]",
                # Help message
                help=" Enter the vswitch to use - either OVS or VPP",
                # List of validators to run on the input
                validators=(wiz.required_validator)
            ),
            wiz.WizardStep(
                id='nics',
                name="NICs to Whitelist: " + devices,
                help="Enter the list (separated by comma) of PCI-IDs",
                validators=(wiz.required_validator),
            ),
            wiz.WizardStep(
                id='topology',
                name="What trafficgen to use?",
                help="Enter the trafficgen to use - STC, Ixia, Moongen , T-Rex",
                validators=(wiz.required_validator),
                default="Ixia"
            )
        )
    )
    wiz_trafficconf = wiz.PromptWizard(
        name="Traffic Configuration",
        description="This configuration covers Traffic specifc inputs",
        steps=(
            wiz.WizardStep(
                id='multistream',
                name='Multistream preferred?',
                help="Multistream preference - Yes or No",
                default='No',
                # validators=(wiz.required_validator)
            ),
            wiz.WizardStep(
                id='count',
                name='Number of flows?',
                help="Enter the number of flows - 2 - 1,000,000",
                default='1000',
                # validators=(wiz.required_validator)
            ),
        )
    )
    main_values = wiz_main.run(shell)
    if main_values['vswitch'] == 'OVS':
        wiz_vswitch = wiz.PromptWizard(
            name = "Vswitch Configuration",
            description="Specific configurations of the virtual-Switch",
            steps=(
                wiz.WizardStep(
                    id='ovs-type',
                    name='OVS Type? [Vanilla or DPDK]',
                    help='Enter either Vanilla or DPDK',
                    default='Vanilla',
                ),
            )
        )
    elif main_values['vswitch'] == 'VPP':
        wiz_vswitch = wiz.PromptWizard(

        )

    if wiz_vswitch:
        vswitch_values = wiz_vswitch.run(shell)
    traffic_values = wiz_trafficconf.run(shell)
    nics = main_values['nics']
    nics = nics.split(',')
    for nic in nics:
        print(nic)

if __name__ == "__main__":
    main()
