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
## @deftypefn {Function File} {} drawplot (@var{stats}, @var{varnames})
##
## This function receives as input the @var{stats} struct and the string arguments.
## The first argument after struct must be a time.
##
## @seealso{csv2struct}
## @end deftypefn

function drawplot (stats, varargin)

if (isstruct (stats))
  c = struct2cell (stats);
  varnames = fieldnames (stats);

  cell_legend = cell (1 , nargin - 2);
  if (strcmp (varargin{1, 1} , varnames{1, 1}) == 0)
    error ("drawplot: the second argument must be ""time""");
  else
    for (ii = 2:nargin - 1)
      idx = find (strcmp (varargin{1, ii} , varnames));
      if (! isempty (idx))
        stem (c{1, 1}, c {idx}, "LineWidth", 3);
        datetick ("x", "HH:MM");
        hold all;
        cell_legend(ii - 1) = varnames(idx, 1);
      endif
    endfor
    legend (cell_legend, "location", "southwestoutside");
  endif
else
  error ("drawplot: STATS should be a struct");
endif

endfunction
