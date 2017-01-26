Name:		building-blocks
Version:	0.0.1
Release:	0
License:	Apache-2
Summary:	The Root of All Tizen Meta Packages (building blocks)
Url:		http://tizen.org
Group:		Meta
Source0:	%{name}-%{version}.tar.gz

Suggests:	%{name}-root-Headless
Suggests:	%{name}-root-Kernel

%description
The root of all Tizen building block meta packages.
Every root-level Tizen building block should be included by this.
Any "minimal" reauired packages should be somehow (directly or indirectly)
required (included) by this package.
In Tizen building blocks, "Requires" means mandatory package.
"Suggests" means optional package.
"Recommened" is reserved for future usage.
"Conflicts" is to unselect unconditionally.
%files


%package root-Headless
Summary:	Enable Tizen Headless Device
Conflicts:	efl
Conflicts:	wayland
Requires:	%{name}-sub1-Headless-Minimal
%description root-Headless
Enableing this means that you are going to create Tizen headless device.
This disables all display depending packages.
%files root-Headless

%package sub1-Headless-Minimal
Summary:	Minimal Tizen Image Configuration for Headless
Requires:	bash
Requires:	systemd
%description sub1-Headless-Minimal
Include minimal set of packages for headless.
%files sub1-Headless-Minimal


# Note to S-Core
# 1. How are you going to make "Radio Button" UI for "choose one among these" case?
#   ; root-Kernel has Requires supplied by Suggests for that case
# 2. How are you going to support Requires/Suggests on virtual packages?
%package root-Kernel
Summary:	Linux Kernel
Requires:	linux-kernel >= 3.10
Suggests:	arm64-tm2-linux-kernel
Suggests:	arm-odroidxu3-linux-kernel

%description root-Kernel
Include Linux Kernel in the Platform Image
%files root-Kernel
