## Copyright 2016 Domenico Enrico Contino
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

function draw_traffic (varargin)

  function [a,b,c,d] = funk (filename)

    [t, src, dst, bytes] = textread (filename, "%s %s %s %d", "delimiter", ",", "headerlines", 1);
    
    # date-wizard
    idx = [0];
    dayz = 0;
    for (ii = 2:numel (t))
      # adds 1 everytime clock goes past midnight
      if (str2num(strtok(t{ii},":")) >= str2num(strtok(t{ii-1},":")))
        idx(ii) = dayz;
      else
        idx(ii) = ++dayz;
      endif
    endfor
    
    # creates timestamps midnight-aware
    dummy_date = datenum(date(), 29);
    for (ii = 1:numel (t))
      t {ii} = ...
        str2num([strrep(datestr(addtodate(dummy_date,idx(ii),"day"),29), "-",","),",",(strrep(t{ii},":",","))]);
    endfor
    # funk ret values
    a = t; b = src; c = dst; d = bytes;
  endfunction # funk

  function graph = graph_creator2 (t, v, bytes, node)
    # search "node" in "v" and saves indexes to "idx"
    indexes = strcmp (node, v);
    idx = find (indexes == 1);

    if (numel (idx) <= 100)
      BLOCK_SIZE = numel (idx);
    else
      BLOCK_SIZE = round (numel (idx) / 10);
    endif

    listPtr = 1; # points 1st free row
    step = t_scale;
    t_notraf = etime (t{idx(1)}, t_base);
    
    if (t_notraf > t_scale) # if traffic starts after 1st time-step
      listPtr = ceil (t_notraf / t_scale) + 1;

      if (listPtr > BLOCK_SIZE)
        graph = zeros (listPtr, 2);
      else
        graph = zeros (BLOCK_SIZE, 2);
      endif
      # fills columns of matrix
      delay = listPtr - 2;
      graph(1:listPtr-1, 1) = 0:t_scale:delay*t_scale;
      step *= listPtr-1;
    else
      graph = zeros (BLOCK_SIZE, 2);
    endif

    listSize = size (graph, 1);
    ii = 1;
    t_from = 1;
    
    while (ii < numel (idx))
      t_delta = etime (t{idx(ii)}, t_base);
      
      if (t_delta > step)
        graph(listPtr, :) = [step (sum(bytes(idx(t_from):idx(ii-1))) / y_scale)];
        
        t_from = ii;
        step += t_scale;
        listPtr += 1;
        # adds new block of memory if needed
        if(listPtr+(BLOCK_SIZE/10) > listSize) # <10%*BLOCK_SIZE
          listSize += BLOCK_SIZE; # adds new slot
          graph(listPtr:listSize, :) = 0;
        endif
      else
        ++ii;
      endif
    endwhile # deltas
    # "rescues" last bytes
    graph(listPtr, :) = [step (sum(bytes(idx(t_from):idx(ii-1))) / y_scale)];    
    graph(listPtr:end, :) = []; # frees unused memory
   
  endfunction # graph_creator2

### MAIN ###
t_scale = 5; # seconds
y_scale = 1000; # KBytes
tic();

# input check & setup
if (nargin < 1)
  usage ("draw_traffic [-s] [NODE_NAME(S)]");
endif

if (strcmp("-s", varargin{1}))
  save_flag = true;
  nni = 2; # node names start index
else
  save_flag = false;
  nni = 1;
endif

for k = nni:nargin
  node_names{end+1} = varargin{k};
endfor

# strings
file_in = ["dump.", node_names{1}, ".IN.csv"];
file_out = ["dump.", node_names{1}, ".OUT.csv"];

c = 0; # switchcase var
if (exist(file_in, "file") != 0)
  [t_in, src_in, dst_in, bytes_in] = funk(file_in);
  c = 1;
else
  printf("draw_traffic: %s doesn't exist\n", file_in);
endif

if (exist(file_out, "file") != 0)
  [t_out, src_out, dst_out, bytes_out] = funk(file_out);
  c += 2;
else
  printf("draw_traffic: %s doesn't exist\n", file_out);
endif

switch (c)
  case (1)
    t_base = t_in{1};
  case (2)
    t_base = t_out{1};
  case (3)
    t_base = min(t_in{1}, t_out{1});
  otherwise
    error ("draw_traffic: both input files don't exist\n");
endswitch  

# plotting
for k = 1:numel (node_names) # first round is for GLOBAL TRAFFIC

  figure; hold on; grid on;
  xlabel ("Time [s]");
  ylabel (["Throughput [KBytes / ", num2str(t_scale), "s]"]);
  
  if ( k == 1 ) # global graph
    plot_eps = ["plot.", node_names{1}, ".global.eps"];
    plot_title = [node_names{1}, " (global)"];
    graph_in = graph_creator2 (t_in, dst_in, bytes_in, node_names{1});
    graph_out = graph_creator2 (t_out, src_out, bytes_out, node_names{1});
  else
    plot_eps = ["plot.", node_names{1}, "-", node_names{k}, ".eps"];
    plot_title = [node_names{1}, " - ", node_names{k}];
    graph_in = graph_creator2 (t_in, src_in, bytes_in, node_names{k});
    graph_out = graph_creator2 (t_out, dst_out, bytes_out, node_names{k});
  endif
  
  title (plot_title);
  plot (graph_in(:,1), graph_in(:,2), "1;IN;", 'linewidth', 1.0);
  plot (graph_out(:,1), graph_out(:,2), "2;OUT;", 'linewidth', 1.5);
  
  if (save_flag)
    print("-depsc2", plot_eps)
  endif
  
  hold off;

endfor

printf("draw_traffic: DURATION = %.3f secs\n", toc());

endfunction
