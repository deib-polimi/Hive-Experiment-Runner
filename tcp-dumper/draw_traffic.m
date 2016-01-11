function draw_traffic (varargin)

  function [a,b,c,d] = funk (filename)

    [t, src, dst, bytes] = textread (filename, "%s %s %s %d", "delimiter", ",", "headerlines", 1);
    
    # date-wizard
    idx = [0];
    dayz = 0;
    for (ii = 2:numel (t))
      # adds 1 everytime the clock goes past midnight
      if ( str2num(strtok(t{ii},":")) >= str2num(strtok(t{ii-1},":")) )
        idx(ii) = dayz;
      else
        idx(ii) = ++dayz;
      endif
    endfor
    
    # creates timestamps midnight-aware
    dummy_date = datenum(date(), 29);
    for (ii = 1:numel (t))
      t {ii} = ...
        str2num(horzcat(strrep(datestr(addtodate(dummy_date,idx(ii),"day"),29),"-",","),",",(strrep(t{ii},":",","))));
    endfor
    # funk ret values
    a = t; b = src; c = dst; d = bytes;
  endfunction # funk

  function graph = graph_creator (t, v, bytes, node)

    indexes = strcmp (node, v);
    idx = find (indexes == 1);
    
    graph = [0 0];
    step = t_scale;
    t_from = 1;

    for (ii = 1:numel (idx))
      t_delta = etime (t{idx(ii)}, t{1});

      if (t_delta >= step)
        graph(end+1, 1) = step;
        graph(end, 2) = sum (bytes (t_from:(ii-1))) / 1000; # KBytes

        # vars update
        t_from = ii;      
        step += t_scale;
      endif
    endfor # deltas
  endfunction # graph_creator

### MAIN ###                                                                          ### MAIN ###

t_scale = 5; # throughput time unit [s], for performance purpose
tic();

# input check & setup
if (nargin < 1)
  usage ("draw_traffic [-s] [NODE_NAME(S)]");
endif

if ( strcmp("-s", varargin{1}) )
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
file_in = horzcat ("dump.", node_names{1}, ".IN.csv");
file_out = horzcat ("dump.", node_names{1}, ".OUT.csv");

if ( exist(file_in, "file") != 0 )
  [t_in, src_in, dst_in, bytes_in] = funk(file_in);
else
  printf("draw_traffic: %s doesn't exist\n", file_in);
endif

if ( exist(file_out, "file") != 0 )
  [t_out, src_out, dst_out, bytes_out] = funk(file_out);
else
  printf("draw_traffic: %s doesn't exist\n", file_out);
endif

# first round is for GLOBAL TRAFFIC
for k = 1:numel (node_names)
  
  #inits
  figure;
  hold on;
  grid on;
  xlabel ("Time [s]");
  ylabel (horzcat("Throughput [KBytes / ", num2str(t_scale), "s]"));
  
  if ( k == 1) # global graph
    plot_png = horzcat ("plot.", node_names{1}, ".global.png");
    plot_title = horzcat (node_names{1}, " (global)");
    graph_in = graph_creator (t_in, dst_in, bytes_in, node_names{1});
    graph_out = graph_creator (t_out, src_out, bytes_out, node_names{1});
  else
    # other graphs
    plot_png = horzcat ("plot.", node_names{1}, "-", node_names{k}, ".png");
    plot_title = horzcat (node_names{1}, " - ", node_names{k});
    graph_in = graph_creator (t_in, src_in, bytes_in, node_names{k});
    graph_out = graph_creator (t_out, dst_out, bytes_out, node_names{k});
  endif
  
  title (plot_title);
  plot (graph_in(:,1), graph_in(:,2), "1;IN;", 'linewidth', 1.0);
  plot (graph_out(:,1), graph_out(:,2), "2;OUT;", 'linewidth', 1.5);
  
  if (save_flag)
    print(plot_png);
  endif
  
  hold off;

endfor # cycles n-times according to input

printf("draw_traffic: DURATION = %f secs\n", toc());

# end MAIN

endfunction
