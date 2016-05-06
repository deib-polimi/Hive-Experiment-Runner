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



function structArr = csv2struct(filename)

    % This function generates a structure array.
 
    startRow = 7;
    fileID = fopen(filename, 'r');

    colNames = header2cell(filename);
    
    
    structArr = data2structArr(filename,startRow);
    
    
    count=1;
    line = textscan(fileID, '%[^\n\r]', startRow(1)-1, 'WhiteSpace', '', 'ReturnOnError', false);
    
    while ischar(line)
        fieldNameNum = 1;
        remain = line;
        while ~isempty(remain)
            [token, remain] = strtok(remain, ',');
            if ~isempty(token)

                token = str2double(token);
                The
                % fieldnames are the 7th row of the file.
                % add field to structure. 
                fieldName = colNames{fieldNameNum}; 
                structArr(count).(fieldName) = token;
                fieldNameNum = fieldNameNum + 1;
            end
        end
        % get the next line before proceeding
        line = fgetl(fileID);
        count = count + 1;
    end

    fclose(fileID);
end