# Maintainer: TBD: This is temporary block for TDC Demo. You may proceed with this later anyway.
# You need ACK (+1) from the maintainer to be reviewed by building-blocks maintainers.

#################
## Smartthings ##
#################
%package sub1-domain_Feature-Smartthings_App
Summary:	Smartthing App support packages
Requires: building-blocks-sub2-domain_API-Network-SoftAP
Requires: building-blocks-sub2-domain_API-AppFramework-Alarm_API
Requires: building-blocks-sub2-domain_API-Security-Device_Certificate
Requires: building-blocks-sub2-domain_API-AppFramework-Message_Port_API
Requires: building-blocks-sub2-domain_API-AppFramework-RPC_Port_API
Requires: smartthings-thing-service
%description sub1-domain_Feature-Smartthings_App
Tizen block (set of packages) for supporting to make Smartthings_app
%files sub1-domain_Feature-Smartthings_App
