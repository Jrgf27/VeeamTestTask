
import sys, os
import shutil
import logging
from datetime import datetime, timedelta


class FolderSynchronizer(object):

    def __init__(self,sourcePath, replicaPath, syncTimeInterval, logFilePath):
        self.processRunning=True
        self.syncTimeInterval=float(syncTimeInterval)
        self.sourceFolderName= os.path.split(sourcePath)[-1]
        self.sourcePath = sourcePath
        self.replicaPath = replicaPath

        self.replicaFolderName=f"{self.sourceFolderName}Replica"
        self.replicaFolderPath = os.path.join(replicaPath,self.replicaFolderName)
        if not os.path.exists(self.replicaFolderPath):
            os.makedirs(self.replicaFolderPath)

        if not os.path.exists(logFilePath):
            os.makedirs(logFilePath)
        logFile=os.path.join(logFilePath, "loggingSynchronization.log")
        logging.basicConfig(filename=logFile, level=logging.INFO)

    def run(self):
        while self.processRunning:
            time_next=datetime.now() + timedelta(minutes=self.syncTimeInterval)
            logMessage=f"Date: {datetime.now()};\t Starting new synchronization"
            logging.info(logMessage)
            print(logMessage)

            self.FolderContentRecursion(self.sourcePath, self.replicaFolderPath)

            logMessage=f"Date: {datetime.now()};\t Finished synchronization, next at {time_next}"
            logging.info(logMessage)
            print(logMessage)

            while datetime.now() < time_next:
                pass

            if not os.path.exists(self.sourcePath):
                logMessage=f"Date: {datetime.now()};\t Source Directory not present, terminating synchronization"
                logging.error(logMessage)
                print(logMessage)
                self.processRunning=False

    def FolderContentRecursion(self, sourcePath, replicaPath):

        sourceFolderContent = [content for content in os.listdir(sourcePath)]
        replicaFolderContent= [content for content in os.listdir(replicaPath)]

        for replicaContent in replicaFolderContent:
            if replicaContent not in sourceFolderContent:
                replicaContentToRemove=os.path.join(replicaPath,replicaContent)
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


        for sourceContent in sourceFolderContent:
            newSourcePath = os.path.join(sourcePath, sourceContent)

            if os.path.isdir(newSourcePath):
                
                newReplicaPath = os.path.join(replicaPath, sourceContent)
                if not os.path.exists(newReplicaPath):
                    logMessage=f"Date: {datetime.now()};\t Creating folder on replica: {newReplicaPath}"
                    logging.info(logMessage)
                    print(logMessage)
                    os.makedirs(newReplicaPath)
                self.FolderContentRecursion(newSourcePath,newReplicaPath)

            else:
                shutil.copy2(newSourcePath,replicaPath)
                logMessage=f"Date: {datetime.now()};\t Copying file to replica: {replicaPath + os.sep + sourceContent}"
                logging.info(logMessage)
                print(logMessage)


if __name__ == '__main__':

    if len(sys.argv)!=5:
        print("Please include the following arguments in this format:\nSource File Path; Replica File Path; Synchronization Time Interval (minutes); Log File Path;")

    elif sys.argv[1] in sys.argv[2]:
        print("Please do not place the Replica directory inside the Source directory")
        print(f"Source Directory:\t {sys.argv[1]}\nReplica Directory:\t {sys.argv[2]}")

    elif not os.path.exists(sys.argv[1]):
        print("Please select a valid Source Directory")

    elif not os.path.exists(sys.argv[2]):
        print("Please select a valid Replica Directory")

    elif not os.path.exists(sys.argv[4]):
        print("Please select a valid Logging File Directory")

    elif not sys.argv[3].isdigit():
        print("Please input a valid Synchronization Time Interval (minutes). Only positive integers or float values allowed")

    else:
        syncFolder = FolderSynchronizer(replicaPath=sys.argv[2],
                                        sourcePath=sys.argv[1],
                                        syncTimeInterval=sys.argv[3],
                                        logFilePath=sys.argv[4])
        
        syncFolder.run()