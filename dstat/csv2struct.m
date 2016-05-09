%% Copyright 2016 Saeid Shams
% 
% Licensed under the Apache License, Version 2.0 (the "License");
% you may not use this file except in compliance with the License.
% You may obtain a copy of the License at
% 
%     http://www.apache.org/licenses/LICENSE-2.0
% 
% Unless required by applicable law or agreed to in writing, software
% distributed under the License is distributed on an "AS IS" BASIS,
% WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
% See the License for the specific language governing permissions and
% limitations under the License.


function stats_struct = csv2struct(filename)

    %   csv2struct function imports and reads a .csv file with a single line of comma separated
    %   text headers followed by many rows of numeric data into a structure array.
    %   Run --> type code to run:
    %   Example:
    %   dstats = csv2struct('stats.master1.csv');

    if nargin < 2
        startRow = 7;
        delimiter = ',';
    else
        error('csv2strct requires 1 arguments.\n');
    end
    
    fileID =fopen(filename,'r');
    
    for i = 1:startRow
        headers = fgetl(fileID);
    end
    
    % Parse the header string into separate headers
    headcell = textscan(headers ,'%q','delimiter',delimiter);
    headcell = headcell{1};
    
    % Read the first line of data to determine the column data types
    data = textscan(fileID,'%s',length(headcell),'delimiter',delimiter);
    data = data{1};
    
    stats_struct = [];
    
    strFormat = [];
    for i = 1:length(data)
        % If str2double returns a numeric value, so the column will be numeric,
        % otherwise if str2num returns empty, so the column will be text
        if ~isnan(str2double(data{i}))
            colFormat = '%f ';
        else
             colFormat = '%q ';

        end
        strFormat = [strFormat colFormat];  %#ok<AGROW>
    end
    
    % restart from the first line of file
    frewind(fileID);
    
    % use the new column format to read the file
    data = textscan(fileID,strFormat,'delimiter',delimiter,'headerlines',startRow);
    fclose(fileID);
    
    for i = 1:length(data)
        
        header = headcell{i};
        

        % Remove ( " ) parts of headers
        header = strrep(header,'"','');

        
        if i ~= 1   
            stats_struct.(header) = data{i};
        else
%           data{i} = datenum(data{i}, 'dd-MM HH:mm:ss');
            data{i} = datetime(data{i},'InputFormat','dd-MM HH:mm:ss')
%           data{i} = cell2struct(data{i}, 'time' ,2);
%           data{i} = todatenum(data{i});  
            stats_struct.(header) = data{i};

        end
        
    end
  

 
   
    
    
    
    
