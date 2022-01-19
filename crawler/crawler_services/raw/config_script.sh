# -------------------------- constants ------------------------------------------------------------------------------------ #

# Keys
key_1='build'
# Commands
command_1='build-tor'
command_2='rebuild-tor'
command_3='build-torrc'
command_4='start-tor'
command_5='build-start-tor'
# Messages
message_1='gcrawl-shell: tor not built... building tor'
message_2='gcrawl-shell: default file copied successfully. Running Configure'
message_3='gcrawl-shell: updating torrc file'
message_4='gcrawl-shell: checking tor configuration'
message_5='gcrawl-shell: configuration finished starting Tor'
message_6='gcrawl-shell: no executable command found'
message_7='gcrawl-shell: tor already build'
message_8='gcrawl-shell: tor not build'
message_9='gcrawl-shell: tor build successfully'
m_tor_directory="$1"         # - default C:/Workspace/Repository/TorBrowser
m_crawl_command="$2"         # - Crawl Command | See reference of commands above
m_tor_connection_port="$3"   # - Default Socks Connection Port | 905 +1
m_tor_control_port="$4"      # - Default Control Port | 905 +2
# Script Base Path
base_path=$(readlink -f "$0")
base_path=$(dirname "$base_path")
# base_path="c://${base_path:12}"
# Build File Location
m_build_file="$m_tor_directory/build-status"
# Torrc File Location
m_torrc_directory="$m_tor_directory/torrc_files/"
# Default Build File Location
m_build_file_default="$base_path/build_status_default"
# Default Torrc File Location
m_torrc_file_default="$base_path/torrc_default"
# Data File Location
m_data_directory="$m_tor_directory\data_files\\"
invokeTorrcBuild(){
echo "$message_3"
mkdir -p "$m_torrc_directory"
mkdir -p "$m_data_directory"
cp -fr "$m_torrc_file_default" "$m_torrc_directory""torrc_$m_tor_connection_port"
appendFile "ControlPort $m_tor_control_port" "$m_torrc_directory""torrc_$m_tor_connection_port"
appendFile "SOCKSPort $m_tor_connection_port" "$m_torrc_directory""torrc_$m_tor_connection_port"
appendFile "DataDirectory $m_tor_connection_port" "$m_torrc_directory""torrc_$m_tor_connection_port"
}
# Terminal Commands - Install Tor
buildTor () {
  # Building Files
  echo "$message_1"
	set -e
	cd "$m_tor_directory"
	./configure
	make clean
	make
	make install
	:
  # Copying Built Files
  echo "$message_2"
}
# $1 build key
# $2 build file path
updateBuildFile(){
  sed -i "1 s/^$1=.*$/$1=$2/" "$3"
}
appendFile(){
  echo "$1" >> "$2"
  cat "$2"
}
# Terminal Commands - Start Tor
invokeStart() {
	echo "$message_5"
	set -e
	# shellcheck disable=SC2086
	cd $m_tor_directory
	tor -f "torrc_files/torrc_$m_tor_connection_port"
	:
}
# Version Checker
invokeTorBuild() {
  echo "$message_4"
  if [ "$1" == "false" ]; then
    updateBuildFile "$key_1" "false" "$m_build_file"
		buildTor
    updateBuildFile "$key_1" "true" "$m_build_file"
    echo "$message_9"
  else
    echo "$message_7"
	fi
}
# Init Enviornment
initEnviornment(){
  cp -n "$m_build_file_default" "$m_build_file"
  source "$m_build_file"
  #build=${build::-1}
}
# -------------------------- Entry Point ---------------------------------------------------------------------------------#
initEnviornment
if [ "$m_crawl_command" == "$command_1" ]; then
  invokeTorBuild "$build"
elif [ "$m_crawl_command" == "$command_2" ]; then
  invokeTorBuild "false"
elif [ "$m_crawl_command" == "$command_3" ]; then
  invokeTorrcBuild
elif [ "$m_crawl_command" == "$command_4" ]; then
  if [[ "$build" == true* ]]; then
    invokeStart
  else
    echo "$message_8"
  fi
elif [ "$m_crawl_command" == "$command_5" ]; then
  if [[ "$build" == true* ]]; then
    invokeTorrcBuild
    invokeStart
  else
    echo "$message_8"
  fi
else
  echo "$message_6"
fi
