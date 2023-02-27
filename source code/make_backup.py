import shutil

source_file = r"C:\Windows\System32\drivers\etc\hosts"  # change this to the location of the hosts file on your system
destination_file = "./hosts"

# Copy the hosts file to the current directory
shutil.copyfile(source_file, destination_file)

print("Hosts file backed up successfully!")
