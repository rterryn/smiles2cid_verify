# smiles2cid_verify
This is example code for a class of functions used to retrieve PubChem CID and name based on molecular structure input. It employs the PUGREST API standardization and record retrieval service based on SMILES input (a popular string representation of molecular structure). The functions were taken from a "molecule standardization" pipeline sub-routine that verifies a SMILES-to-CID relationship against PubChem records. The purpose is to verify this relationship for molecules and CIDs submitted for registration into the LINCS library of molecules. The molecules and CIDs are submitted from experimental labs, and this pipeline attempts to catch errors or discrepancies between the submitted structure and the intended CID and name.

# running the code
The code is written in Python3 and contains an example main loop. There is no packaged environment, but the code can be executed from the command line if Python3 is installed locally and configured on the system path. Most Python3 packages, e.g., Anaconda, contain all the required libraries except possibly the 'requests' library which may be installed via the site directions <http://docs.python-requests.org/en/master/user/install/ . An example input file is included in the repository. To test, execute smiles2cid_verify.py from the same folder as the input file.

#input and output details
