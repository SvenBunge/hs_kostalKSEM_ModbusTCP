#!/bin/bash
(cd ../../; python2 ./generator.pyc hs_kostalKSEM_ModbusTCP utf-8)
markdown2 --extras tables,fenced-code-blocks,strike,target-blank-links doc/log14181.md > release/log14181.html
(cd release; zip -r 14181_kostalKSEM_ModbusTCP.hslz *)
