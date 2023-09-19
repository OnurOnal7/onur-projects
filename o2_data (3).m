
data = csvread('Glovebox_test_3-17.csv'); % Reads table

data = data * 100; % Converts to PPM

% Reading rate and array size
r = 5;    
l = size(data);

% Loop to handle jump spots
for i = 2:1:l
    if abs(data(i) - data(i - 1)) > 50000
        for j = i:1:l
            data(j) = data(j) / 250;
        end
    end 
end

column = 0:r:r*(l-1); % Creates vector of values

avgO2 = mean(data);
average = ones(l).*avgO2; %ones() will only create vector i.e. one row

% Finds Max and Min values in data array
[Max, Max_Idx] = max(data, [], 'all', 'linear'); 
[Min, Min_Idx] = min(data, [], 'all', 'linear');

% Finds corresponding index of Max and Min values
Max_Idx_Plot = Max_Idx * r;
Min_Idx_Plot = Min_Idx * r;  

% Plotting x and y axis
semilogy(column, data, 'black') % Use semilogy instead of plot
xlabel("Time (ms)")
ylabel("O2 Level (PPM)")
title("O2 Level vs. Time for Glovebox")

hold on

semilogy(column, average, 'blue') % Use semilogy for the average data too

hold on

% Plotting Max and Min
semilogy(Max_Idx_Plot, Max,'r*', 'Color', 'red')  
semilogy(Min_Idx_Plot, Min, '*', 'Color', 'magenta')

legend("O2 Level", "Average", "Maximum","Minimum") % Legend
