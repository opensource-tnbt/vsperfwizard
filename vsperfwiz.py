from __future__ import print_function
from pypsi import wizard as wiz
from pypsi.shell import Shell
import nicinfo
import signal
import sys

class VsperfWizard():
    """
    Class to create wizards
    """
    def __init__(self):
        self.shell = Shell()

######## Support Functions ############################
    def get_nicpcis(self):
        self.rhi = nicinfo.RemoteInfo(self.dut_values['dutip'],
                                      self.dut_values['dutuname'],
                                      self.dut_values['dutpwd'])
        dev_list = self.rhi.get_nic_details()
        self.devices = ''
        index = 0
        for dev in dev_list:
            self.devices += str("("+str(index)+")"+ " "
                                + str(dev["Slot"]) + ', ')
            index = index +1

############# All the Wizards ##################################

    def dut_wizard(self):
        self.wiz_dut = wiz.PromptWizard(
            name="VSPERF DUT Info Collection",
            description="This collects DUT info",
            steps=(
                # The list of input prompts to ask the user.
                wiz.WizardStep(
                    # ID where the value will be stored
                    id="dutip",
                    # Display name
                    name="Enter the IP address of the DUT [local]",
                    # Help message
                    help= "IP address of the DUT host",
                    # List of validators to run on the input
                    validators=(wiz.required_validator)
                ),
                wiz.WizardStep(
                    # ID where the value will be stored
                    id="dutuname",
                    # Display name
                    name="Enter the username to connect to DUT",
                    # Help message
                    help= "Username for DUT host",
                    # List of validators to run on the input
                    validators=(wiz.required_validator)
                ),
                wiz.WizardStep(
                    # ID where the value will be stored
                    id="dutpwd",
                    # Display name
                    name="Enter the Password to connect to DUT",
                    # Help message
                    help= "Password for the DUT host",
                    # List of validators to run on the input
                    validators=(wiz.required_validator)
                ),
            )
        )

    def main_wizard(self):
        # First get the nics.
        self.get_nicpcis()
        self.wiz_main = wiz.PromptWizard(
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
                    name="NICs to Whitelist: " + self.devices,
                    help="Enter the list (separated by comma) of PCI-IDs",
                    validators=(wiz.required_validator),
                ),
                wiz.WizardStep(
                    id='topology',
                    name="What trafficgen to use?",
                    help="Enter the trafficgen to use - STC, Ixia, Moongen, T-Rex",
                    validators=(wiz.required_validator),
                    default="T-Rex"
                )
            )
        )

    def traffic_wizard(self):
        self.wiz_traffic = wiz.PromptWizard(
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

    def ovs_wizard(self):
        self.wiz_ovs = wiz.PromptWizard(
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

    def vpp_wizard(self):
        self.wiz_vpp = wiz.PromptWizard(
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

############### All the Run Operations ######################

    def run_dutwiz(self):
        self.dut_wizard()
        self.dut_values = self.wiz_dut.run(self.shell)

    def run_mainwiz(self):
        self.main_wizard()
        self.main_values = self.wiz_main.run(self.shell)

    def run_vswitchwiz(self):
        if self.main_values['vswitch'] == 'OVS':
           self.ovs_wizard()
           self.ovs_values = self.wiz_ovs.run(self.shell)
        elif self.main_values['vswitch'] == 'VPP':
            self.vpp_wizard()
            self.vpp_values = self.wiz_vpp.run(self.shell)

    def run_trafficwiz(self):
        self.traffic_wizard()
        self.traffic_value = self.wiz_traffic.run(self.shell)

################ Prepare Configuration File ##################

    def prepare_conffile(self):
        with open("./vsperf.conf", 'w+') as ofile:
            ofile.write("#### This file is Automatically Created")


def signal_handler(signal, frame):
    print("\n You interrupted, No File will be generated!")
    sys.exit(0)


def main():
    try:
        vwiz = VsperfWizard()
        vwiz.run_dutwiz()
        vwiz.run_mainwiz()
        vwiz.run_vswitchwiz()
        vwiz.run_trafficwiz()
        vwiz.prepare_conffile()
    except (KeyboardInterrupt, MemoryError):
        print("Some Error Occured, No file will be generated!")

    print("Thanks for using the VSPERF-WIZARD, Please look for vsperf.conf \
          file in the current folder")


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    main()
