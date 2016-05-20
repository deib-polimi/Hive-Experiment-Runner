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

function drawplot(strt , varargin)

    % This function receives as input a struct and the string argoments.
    % The first argoment after struct must be a time.
    %   Type code to run:
    %   Example:      
    %         drawplot(strt,'time','usr','sys','idl','wai')

    if ~isstruct(strt)
      msgerror = strcat('''',inputname(1),''''' is not a structure!!');
      error(msgerror);
    end
%   varargin = cell 1x4 : varargin{1,1}, varargin{1,2}....
    c = struct2cell(strt); %15x1 cell array value= c{1,1},c{2,1},...
    varnames = fieldnames(strt); % 15x1 cell names , time=varnames{1,1} , usr=varnames{2,1},..

    cellLegend = cell(1 , length(varargin)-1);  %initialize of cell array to use in Legend().
    if strcmp(varargin{1,1} , varnames{1,1}) == 0  % the first argoment after struct must be 'time' .
        msgerror = strcat('''',varargin{1,1},''''' is not a time!! The first argoment after struct must be time.');
        error(msgerror);
    else
        for i=2:length(varargin)  % i=2 because the first argoment is time.
                idx = find(strcmp(varargin{1,i} , varnames));
                if ~isempty(idx)
                    stem(c{1,1},c{idx}  , 'LineWidth',3); 
                    datetick('x','HH:MM');
                    hold all;
                    cellLegend(1,i-1) = varnames(idx,1);
                    hold all;
                end
         end
         legend (cellLegend, 'location', 'southwestoutside');
    end

