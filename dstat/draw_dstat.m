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
## @deftypefn {Function File} {} draw_dstat (@var{stats}, @var{fields})
## @deftypefnx {Function File} {} draw_dstat (@var{stats}, @var{fields}, @var{x})
##
## Plot data in the @var{stats} struct.
## @var{fields} is a cell array of strings containing the field names to plot.
## The x-axis defaults to "time", but you can optionally override this
## behavior with the third optional argument.
##
## @seealso{csv2struct}
## @end deftypefn

function draw_dstat (stats, fields, x)

if (isstruct (stats))
  if (iscellstr (fields))
    if (nargin == 3)
      if (ischar (x))
        time = false;
      else
        error ("draw_dstat: X should be a string");
      endif
    else
      time = true;
      x = "time";
    endif
    x = stats.(x);

    figure;
    hold all;
    for (ii = 1:numel (fields))
      field = fields{ii};
      stem (x, stats.(field), "LineWidth", 3);
      if (time)
        datetick ("x", "HH:MM");
      endif
    endfor

    grid on;
    legend (fields, "location", "eastoutside");
  else
    error ("draw_dstat: FIELDS should be a cell array of strings");
  endif
else
  error ("draw_dstat: STATS should be a struct");
endif

endfunction
