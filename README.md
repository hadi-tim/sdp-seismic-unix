## Table of contents
### 1. [How to install Seismic Unix on Windows](#Introduction)
### 2. [Ubuntu on Windows](#paragraph1)
### 3. [Installing Xming Server](#subparagraph1)
### 4. [Installing Seismic Unix](#install)
.

.

.

.

.

.

.

.

.

.

.

.

### 1. How to install Seismic Unix on Windows
This tutorial will illustrate step by step on how to process seismic data using Seismic Unix. Before starting our Seismic Data Processing journey, some installations need to be made. We will go through all**
### 2. Ubuntu on Windows

The perfect thing to do is to install a Linux partition in your machine (laptop or desktop). In my case I installed Ubuntu [WSL](https://ubuntu.com/wsl) which is a complete Ubuntu terminal environment in on Windows, which is called Windows Subsystem for Linux (WSL)

### 3. Installing Xming Server
In order to run SU modules, an X window server will be needed. in our case I used Xming, which need to be launched after installing Seismic Unix. Here is the [Xming server website for download](http://www.straightrunning.com/XmingNotes/)

### 4. Installing Seismic Unix
Before installing SU, we need to set some environment variables. Add following commands to your profile like .zshrc or .bashrc.

```Shell
export CWPROOT=$HOME
```
```Shell
export PATH=$PATH:$HOME/bin
```
Get SU files from [Seismic-unix.org](https://wiki.seismic-unix.org/doku.php). Here we download the latest version of SU cwp_su_all_44R23.tgz.

Copy the file to $HOME and unzip it by:

```Shell
mv /mnt/c/Users/lzhao/Downloads/cwp_su_all_44R26.tgz ~
```
```Shell
tar xvf cwp_su_all_44R26.tgz
```
After extracting the folder of SU a correction need to be made to the config file:
```Shell
cd src
```
```Shell 
mv Makefile.config Makefile.config.old
```
```Shell
cp ./configs/Makefile.config_Linux_x86_64 ./Makefile.config
```
Installing some packages necessary for Seismic Unix.

```Shell
sudo apt install build-essential
```

```Shell
sudo apt install gfortran
sudo apt install libx11-dev
sudo apt install libxt-dev
sudo apt install freeglut3-dev
sudo apt install libxmu-dev libxi-dev
sudo apt install libc6
sudo apt install libuil4
sudo apt install x11proto-print-dev
sudo apt install libmotif-dev
```
Finally we will install Seismic Unix:
```Shell
make install make xtinstall
make finstall
```
Seismic Unix Should be installed successfully without errors, please ignore the warning messages.
In order to check run the command below:
```Shell
suplane | suximage title="test"
```
**CONGRATULATIONS ON YOUR FIRST SEISMIC UNIX DISPLAY!!!**

### 5. Seismic Unix data formats

</details>

<!--
  <<< Author notes: Footer >>>
  Add a link to get support, GitHub status page, code of conduct, license link.
-->

---

Get help: [Post in our discussion board](https://github.com/skills/.github/discussions) &bull; [Review the GitHub status page](https://www.githubstatus.com/)

&copy; 2022 GitHub &bull; [Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/code_of_conduct.md) &bull; [CC-BY-4.0 License](https://creativecommons.org/licenses/by/4.0/legalcode)
