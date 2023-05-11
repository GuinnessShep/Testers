#!/bin/bash

echo "Installing dependencies..."
pkg install python clang wget -y

echo "Installing APKTool..."
wget https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool -O $PREFIX/bin/apktool
wget https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_2.6.0.jar -O $HOME/apktool.jar
chmod +x $PREFIX/bin/apktool
mv $HOME/apktool.jar $PREFIX/bin/

echo "Installing JDK..."
pkg install openjdk-17 -y

echo "Setting up environment variables..."
echo "export JAVA_HOME=/data/data/com.termux/files/usr/libexec/openjdk-17" >> $HOME/.bashrc
echo "export PATH=\$JAVA_HOME/bin:\$PATH" >> $HOME/.bashrc
source $HOME/.bashrc

echo "Installing Python packages..."
pip install frida-tools cryptography

echo "Setup complete!"
