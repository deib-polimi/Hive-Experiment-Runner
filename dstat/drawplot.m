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

function drawplot(strt)

    % drawplot() receive in input struct to plot the fields. use inputparser class 
    % to parsing the varargin.

     if nargin ~=1
        error('drawplot requires 1 struct arguments.\n');
     end
    % creat object
    p = inputParser();
    if ~isstruct(strt)
        error('Input is not string, insert the string name of the variables of workspace.');
    else
        addRequired(p,'x',@isstruct);
    end
    parse(p,strt);
    chois = menu('select a plot:','CPU','NETWORK','MEMORY');
    switch chois
      case 1
        cpuplot(strt.time,strt.usr,strt.sys,strt.idl,strt.wai);
      case 2
        networkplot(strt.time,strt.recv,strt.send);
      case 3
        memoryplot(strt.time,strt.used,strt.buff,strt.cach,strt.free)
    end
    
    % The function to plot Flexiant Cluster CPU last hour
    function cpuplot(time,usr,sys,idl,wai);
        % Create figure
%        figure1 = figure();
        % Create axes
%        axes1 = axes('Parent',figure1);
        plot(time, sys , 'LineWidth',3);
        hold on;
        plot(time, usr , 'LineWidth',3);
        hold on;
        plot(time, idl , 'LineWidth',3);
        hold on;
        plot(time, wai , 'LineWidth',3);
        hold on;
        datetick('x','HH:MM');
        title('Flexiant Cluster CPU last hour');
        ylabel({'Percent'},'HorizontalAlignment','center','FontWeight','bold','FontSize',18);
        legend ('usr','sys','idl','wai', 'location', 'southoutside');
    end
    
    % the function to plot Flexiant Cluster NETWORK last hour.
    function networkplot(time,recv,send)
        plot(time , recv , 'LineWidth',4);
        hold on;
        datetick('x','HH:MM');
        plot(time , send , 'LineWidth',4);
        hold on ;
        datetick('x','HH:MM');
        title('Flexiant Cluster NETWORK last hour');
        ylabel({'Bytes/sec'},'HorizontalAlignment','center','FontWeight','bold','FontSize',18);
        legend ('recv','send', 'location', 'southoutside');
    end
    
    % the function to plot Flexiant Cluster MEMORY last hour.
    function memoryplot(time,used,buff,cach,free)
        clf;
        colororder = get (gca, 'colororder');
        plot(time , used);
        hold on;
        plot(time , buff);
        hold on;
        plot(strt.time , strt.cach);
        hold on;
        plot(time , free);
        hold off;
        datetick('x','HH:MM');
        title('Flexiant Cluster MEMORY last hour');
        ylabel({'Bytes'},'HorizontalAlignment','center','FontWeight','bold','FontSize',18);
        legend ('used','buff','cach','free', 'location', 'southoutside');
    end

end



  
  