
import sys, os
import shutil
import logging
from datetime import datetime, timedelta


class FolderSynchronizer(object):

    #Initializes the FolderSynchronizer object with the 4 required arguments
    def __init__(self,sourcePath, replicaPath, syncTimeInterval, logFilePath):

        #Initializes variables within the object for further use:
        #   processRunning enables or disables the synchronization function of the object depending on it's boolean state
        #   syncTimeInterval converts the string argument passed when calling the python script into a float, to be used with the datetime.timedelta function
        #   sourceFolderName returns the name of the folder to be synchronized, to be used to name the replicated folder in replicaFolderName
        #   replicaFolderPath provides the folder path where the source folder will replicated into

        self.processRunning=True
        self.syncTimeInterval=float(syncTimeInterval)
        self.sourceFolderName= os.path.split(sourcePath)[-1]
        self.sourcePath = sourcePath
        self.replicaPath = replicaPath

        self.replicaFolderName=f"{self.sourceFolderName}Replica"
        self.replicaFolderPath = os.path.join(replicaPath,self.replicaFolderName)

        #Checks if the replica folder path already exists in the system, if it does not then it creates it
        if not os.path.exists(self.replicaFolderPath):
            os.makedirs(self.replicaFolderPath)

        #Checks if the logging file folder path already exists in the system, if it does not then it creates it
        if not os.path.exists(logFilePath):
            os.makedirs(logFilePath)

        #Initializes the logging function, to be written into the file loggingSynchronization.log
        logFile=os.path.join(logFilePath, "loggingSynchronization.log")
        logging.basicConfig(filename=logFile, level=logging.INFO)

    def run(self):

        #Checks if the process is still running, if not the synchronization is terminated
        while self.processRunning:

            #Sets up the time at which the next synchronization is scheduled to occur
            time_next=datetime.now() + timedelta(minutes=self.syncTimeInterval)
            logMessage=f"Date: {datetime.now()};\t Starting new synchronization"
            logging.info(logMessage)
            print(logMessage)

            #Initializes the folder content synchronization recursion function after the appropriate logging messages are printed to the command line and inserted into the log file
            self.FolderContentRecursion(self.sourcePath, self.replicaFolderPath)

            #Lets the user know the synchronization step has finished and when the next synchronization is scheduled to occur
            logMessage=f"Date: {datetime.now()};\t Finished synchronization, next at {time_next}"
            logging.info(logMessage)
            print(logMessage)

            #Waiting for the time for the next synchronization, similar to python sleep function but using datetime instead
            while datetime.now() < time_next:
                pass
            
            #Checks if the folder to be replicated has not been deleted while waiting for the next synchronization. If the folder is not present the synchronization is stopped.
            if not os.path.exists(self.sourcePath):
                logMessage=f"Date: {datetime.now()};\t Source Directory not present, terminating synchronization"
                logging.error(logMessage)
                print(logMessage)
                self.processRunning=False

    def FolderContentRecursion(self, sourcePath, replicaPath):
        
        #Use of list comprehension in python to obtain the content inside the sourcePath and replicaPath directories provided as arguments

        sourceFolderContent = [content for content in os.listdir(sourcePath)]
        replicaFolderContent= [content for content in os.listdir(replicaPath)]

        #We first compare the contents located in the replica folder against the source folder. 
        for replicaContent in replicaFolderContent:

            #If files or folders are present in the replica folder and not in the source folder, these are deleted from the replica directory
            if replicaContent not in sourceFolderContent:
                replicaContentToRemove=os.path.join(replicaPath,replicaContent)

                #We then check if the content is a file or folder respectively and use the appropriate functions for their deletion
                if os.path.isdir(replicaContentToRemove):
                    logMessage=f"Date: {datetime.now()};\t Removing folder tree: {replicaContentToRemove}"
                    logging.info(logMessage)
                    print(logMessage)
                    shutil.rmtree(os.path.join(replicaPath,replicaContent))

                else:
                    logMessage=f"Date: {datetime.now()};\t Removing file: {replicaContentToRemove}"
                    logging.info(logMessage)
                    print(logMessage)
                    os.remove(replicaContentToRemove)

        #The contents located in the source folder directory are checked
        for sourceContent in sourceFolderContent:
            newSourcePath = os.path.join(sourcePath, sourceContent)

            #If the content is a folder directory, we create the new path to be used in the replica folder tree
            if os.path.isdir(newSourcePath):
                newReplicaPath = os.path.join(replicaPath, sourceContent)

                #Then we check if this new path generated already is present in the replica folder tree, if it is not then it is created.
                if not os.path.exists(newReplicaPath):
                    logMessage=f"Date: {datetime.now()};\t Creating folder on replica: {newReplicaPath}"
                    logging.info(logMessage)
                    print(logMessage)
                    os.makedirs(newReplicaPath)

                #Once the replica directory is created, this function is ran recursively with the new source and replica folder directories. 
                #The recursiveness propagates until we reach a folder directory which only contains files
                self.FolderContentRecursion(newSourcePath,newReplicaPath)

            else:
                #If the content within the source folder path contains files, these are copied into the replica folder directory.
                shutil.copy2(newSourcePath,replicaPath)
                logMessage=f"Date: {datetime.now()};\t Copying file to replica: {replicaPath + os.sep + sourceContent}"
                logging.info(logMessage)
                print(logMessage)

#The code below the if statement only runs if the user is running this specific script
#This allows the FolderSynchronizer object to be imported into other scripts as it's own module, while being able to run the script separately if needed
if __name__ == '__main__':

    #Checking if the user has provided 4 arguments when calling the script
    if len(sys.argv)!=5:
        print("Please include the following arguments in this format:\nSource File Path; Replica File Path; Synchronization Time Interval (minutes); Log File Path;")

    #Checking if the user is trying to place the replica folder inside the source directory
    #This can't be allowed due to the recursive function used to replicate the folder. If it was to be allowed, the program would freeze, never leaving the recursive function
    elif sys.argv[1] in sys.argv[2]:
        print("Please do not place the Replica directory inside the Source directory")
        print(f"Source Directory:\t {sys.argv[1]}\nReplica Directory:\t {sys.argv[2]}")

    #Checks if the source folder directory exists in the system
    elif not os.path.exists(sys.argv[1]):
        print("Please select a valid Source Directory")

    #Checks if the replica folder directory exists in the system
    elif not os.path.exists(sys.argv[2]):
        print("Please select a valid Replica Directory")

    #Checks if the logging file folder directory exists in the system
    elif not os.path.exists(sys.argv[4]):
        print("Please select a valid Logging File Directory")

    #Checks if provided argument for synchronization time interval is a positive integer or float, as required for the datetime function in which it is used.
    elif not sys.argv[3].isdigit():
        print("Please input a valid Synchronization Time Interval (minutes). Only positive integers or float values allowed")

    #If all checks are passed, the object is created and the user executes its run() function
    else:
        syncFolder = FolderSynchronizer(sourcePath=sys.argv[1],
                                        replicaPath=sys.argv[2],
                                        syncTimeInterval=sys.argv[3],
                                        logFilePath=sys.argv[4])
        
        syncFolder.run()