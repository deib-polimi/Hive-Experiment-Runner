## Copyright 2016 Saeid Shams
## Copyright 2016 Eugenio Gianniti
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.

## -*- texinfo -*-
## @deftypefn {Function File} {} struct2vars (@var{stats})
##
## Extract values from @var{stats} fields to workspace variables.
##
## @end deftypefn

function struct2vars (stats)

if (isstruct (stats))
  names = fieldnames (stats);
  for (ii = 1:numel (names))
    assignin ("caller", names{ii}, stats.(names{ii}));
  endfor
else
  error ("struct2vars: STATS should be a struct");
endif

endfunction
