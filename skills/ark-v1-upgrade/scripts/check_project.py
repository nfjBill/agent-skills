#!/usr/bin/env python3
"""Read-only ARK migration inventory. Never execute config or expose env values."""
import argparse,json,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('project',type=Path);args=p.parse_args()
root=args.project.resolve();findings=[];packages=[]
node_version_files=[]
version_file_names={'.nvm','.nvmrc','.node-version'}
skip={'node_modules','.git','dist','dist-types','.cache','coverage','artifacts','tmp'}
def inspect_node_version(text):
 # Inventory only: never source shell code or execute a version manager.
 values=[line.split('#',1)[0].strip() for line in text.splitlines()]
 values=[value for value in values if value]
 if len(values)!=1:return {'requested':None,'status':'needs-review'}
 value=values[0]
 match=re.fullmatch(r'v?(\d+)(?:\.(\d+))?(?:\.(\d+))?(?:-([0-9A-Za-z.-]+))?(?:\+[0-9A-Za-z.-]+)?',value)
 if not match:
  if re.fullmatch(r'(?:node|stable|system|lts(?:/[a-zA-Z0-9*-]+)?)',value):return {'requested':value,'status':'needs-resolution'}
  return {'requested':None,'status':'needs-review'}
 if any(part is not None and len(part)>1 and part.startswith('0') for part in match.group(1,2,3)):
  return {'requested':value,'status':'needs-review'}
 major=int(match[1]);minor=int(match[2]) if match[2] is not None else None
 if match[4]:return {'requested':value,'status':'needs-review'}
 if major<20 or major==21 or major==20 and minor is not None and minor<19 or major==22 and minor is not None and minor<12:
  return {'requested':value,'status':'incompatible'}
 if minor is None or match[3] is None:return {'requested':value,'status':'needs-resolution'}
 return {'requested':value,'status':'compatible'}
def walk(base):
 for child in sorted(base.iterdir()):
  if child.is_symlink() or child.name in skip:continue
  if child.is_dir():yield from walk(child)
  elif child.name in version_file_names or child.name=='Dockerfile' or child.suffix in {'.ts','.js','.mjs','.cjs','.json','.yaml','.yml'}:yield child
for file in walk(root):
 relative=str(file.relative_to(root));text=file.read_text(errors='replace')
 if file.name in version_file_names:
  entry={'file':relative,**inspect_node_version(text)};node_version_files.append(entry)
  reasons={'incompatible':'Node version file does not satisfy ARK engines; update the existing file',
           'needs-resolution':'Resolve the Node selector and verify the installed runtime against ARK engines',
           'needs-review':'Review the Node version file format or prerelease; preserve the existing loading convention'}
  if entry['status'] in reasons:findings.append({'file':relative,'reason':reasons[entry['status']]})
 elif file.name=='package.json':
  try:
   d=json.loads(text);packages.append({'path':relative,'name':d.get('name'),'node':d.get('engines',{}).get('node'),'ark':{k:v for k,v in {**d.get('dependencies',{}),**d.get('devDependencies',{})}.items() if k in {'arkc','arkclib','ark-plus','pxnpm'}},'scripts':d.get('scripts',{})})
  except json.JSONDecodeError:findings.append({'file':relative,'reason':'invalid package.json'})
 elif file.name.startswith('ark.config.') or 'plugin' in relative.lower() or file.name in {'Dockerfile','docker-compose.yml'}:
  for regex,reason in [(r'@rspack/core/dist/','private core import'),(r'@arkcbuild/[^\s\x27\x22]+/dist','private build engine import'),(r'\b(?:webpackChain|modifyWebpackConfig|bundlerType\s*:\s*[\x27\x22]webpack)','webpack-only extension'),(r'\.rule\([^\n]+\)\.uses','root rule loader inspection'),(r'node:(?:1[0-9]|20\.(?:[0-9]|1[0-8]))(?:[^0-9]|$)','Node image below V2 minimum')]:
   if re.search(regex,text):findings.append({'file':relative,'reason':reason})
print(json.dumps({'root':str(root),'requiredNode':'^20.19.0 || >=22.12.0','nodeVersionFiles':node_version_files,'packages':packages,'review':findings},ensure_ascii=False,indent=2))
