import os
import sys
import optparse
import shutil
import re
import csv

debug = True
def copy_evidence(source, target):
  """Copy <source> file/directory to <target> directory"""
  global debug
  print "[*] Verifying source and target validity"
  if (not os.path.isfile(source)) & (not os.path.isdir(source)):
    print "[-] Invalid source or source not found"
    return False
  
  print "[*] Copying file..."
  if (os.path.isfile(source)):
    if (not os.path.isdir(target)):
      try:
        os.makedirs(target)
      except:
        pass
    print "[+] Copying " + source + " to " + target
    head, tail = os.path.split(source)
    if not(os.path.isfile(target+'/'+tail)):
      shutil.copy(source, target)
  if (os.path.isdir(source)):
    try:
      head, tail = os.path.split(source)
      target_revised = os.path.join(target,tail)
      if (not os.path.isdir(target_revised)):
        shutil.copytree(source, target_revised)
      else:
        target_revised = os.path.join(target_revised,'bulk') #simple hack to allow copytree to copy dir when parent target is already exist
        shutil.copytree(source, target_revised)
    except OSError as e:
      print "[!] Directory "+ source + " not copied. Error: %s"  %e
      pass	
  return True

def unique_list(alist):
  """Create a new list from an input alist which contain only unique members"""
  uniqued = []
  for a in alist:
    if a not in uniqued:
      uniqued.append(a)
  return uniqued

def extract_reference(ref_code, response):
  """Extract reference from response given the ref_code identifier"""
  global debug
  pattern = re.compile('(?<='+ref_code+')[0-9]{3,4}')
  artefact_nos = re.findall(pattern, response)
  return unique_list(artefact_nos)


def get_locations(artefact_no, artefact_file):
  """Get artefact location from arteface list (csv) file"""
  global debug
  try:
    locations = ''
    with open(artefact_file, 'r') as csvfile:
      artefact_reader = csv.reader(csvfile, dialect='excel')
      for row in artefact_reader:
        if int(artefact_no) == int(row[2]): # To do: change 2 with actual "artefact_location" column index 
          locations = row[5]
          return locations
  except:
    print "[!] Unable to open artefact (csv) file"
    return ''
  
def scan_interim_report(int_report, ref_code):
  """Get pairs of (requirement, [artefact references]) from interim report"""
  global debug
  requirement_artefact_list = []
  try:
    with open(int_report, 'r') as csvfile:
      interim_reader = csv.reader(csvfile, dialect='excel')
      for row in interim_reader:
        references = extract_reference(ref_code, row[3]+' '+row[4]) # To do: Change 3 and 4 to the actual "response" column index
        requirement = row[0] # To do: Change 0 to the actual "requirement" column index
        requirement_artefact_list.append([requirement, references])
      return requirement_artefact_list
  except csv.Error as e:
    sys.exit("[!] Error reading interim report file")
 

def main():
  parser = optparse.OptionParser("Usage %prog -i <interim report> -a <artefact file> -t <target dir> -r <artefact code>")
  parser.add_option('-i', dest = 'int_report', type = 'string', help = 'Specify interim report file')
  parser.add_option('-a', dest = 'art_file', type = 'string', help = 'Specify artefact file')
  parser.add_option('-t', dest = 'target_dir', type = 'string', help = 'Specify target directory')
  parser.add_option('-r', dest = 'art_ref', type='string', help = 'Specify Artefact Reference Code')
  (options, args) = parser.parse_args()
  if (options.int_report == None) | (options.art_file == None) | (options.target_dir == None):
    print parser.usage
    exit(0)
  art_file = options.art_file
  target_dir = options.target_dir
  int_report = options.int_report
  art_ref = options.art_ref
  # open interim report file and get all pair of (requirement, [references])
  print "[*] Extracting requirements and artefact references from interim report ..."
  requirement_artefact_list = scan_interim_report(int_report, art_ref)
  # for each pair of (requirement, [references])
  for ra in requirement_artefact_list:
    requirement = ra[0]
    artefact_list = ra[1]
    for a in artefact_list:
      location = get_locations (a, art_file)
      if debug:
        print "[+] {Requirement:} " + requirement + " {Artefact No:} " + a + " {Location:} " + location
      print "[*] Copying evidence for requirement {"+requirement+"}"
      copy_evidence(location, target_dir + '/' + requirement)
  print "[+] Complete processing " + int_report
if __name__=='__main__':
  main() 
