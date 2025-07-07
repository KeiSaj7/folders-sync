A program that synchronises two folders. It maintains an identical copy of the source folder in the replica folder.
The synchronization is one-way, meaning that after synchronization, the content of the replica folder is modified to exactly match the content of the source folder.
Synchronization is performed periodically, but limited amounts of times. Program stops after last synchronization.
File creation/copying/removal operations are logged to a file and to the console output.
Folder paths, synchronization interval, amount of synchronizations and log file path are provided using the command line arguments.
It is very important that the arguments should be handled in the following order:
- path to source folder
- path to replica folder
- interval between synchronizations 
- amount of synchronizations 
- path to log file
