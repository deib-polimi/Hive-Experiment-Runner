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
## @deftypefn {Function File} {@var{stats} =} csv2struct (@var{filename})
##
## Read dstat data from @var{filename} and return it as a struct, @var{stats}.
##
## @seealso{draw_dstat}
## @end deftypefn

function stats = csv2struct (filename)

if (nargin == 1)
  if (ischar (filename))
    header_rows = 7;
    delimiter = ",";

    fid = fopen (filename, "r");
    fskipl (fid, header_rows - 1);

    % Parse the header string (6th row) into separate headers
    headers = fgetl (fid);
    headcell = textscan (headers, "%s", "delimiter", delimiter);
    headcell = headcell{1};

    % Read the first line of data (7th row) to determine the column data types
    first_row = fgetl (fid);
    data = textscan (first_row, "%s", length (headcell), "delimiter", delimiter);
    data = data{1};

    row_content = [];
    for (ii = 1:length (data))
      if (! isnan (str2double (data{ii})))
        row_content = [row_content, "%f "];
      else
        row_content = [row_content, "%s "];
      endif
    endfor

    frewind (fid);
    data = textscan (fid, row_content, "delimiter", delimiter, "headerlines", header_rows);
    fclose (fid);

    stats = struct();
    for (ii = 1:length (data))
      header = headcell{ii};

      if (header(1) == header(end) && header(end) == '"')
        header = header(2:end - 1);
      endif

      if (ii > 1)
        stats.(header) = data{ii};
      else
        data{ii} = datenum (data{ii} , "dd-mm HH:MM:SS");
        stats.(header) = data{ii};
      endif
    endfor
  else
    error("csv2struct: you should provide a filename as input");
  endif
else
  error("csv2struct requires one argument");
endif

endfunction
