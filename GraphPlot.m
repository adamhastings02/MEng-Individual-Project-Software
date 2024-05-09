% GraphPlot.m
%------------------------------------------------%
% By: Adam Hastings
% Date: 14th April 2024
% Module: ELEC5870M - Individual Project
% Description:
%------------------------------------------------%
% A short program which plots a performance graph
%------------------------------------------------%

% Clear everything
clear; 

% Generate x values
x = 60:60:1120;

% Y values
y = [1.61,1.84,2.26,2.96,3.56,4.19,4.55,5.39,5.85,6.24,6.88,7.39,7.80,8.47,9.06,9.63,10.37,10.98];

% Plot the inductor current curve
figure(1)
fig1 = scatter(x, y, 'bx', 'LineWidth', 1.5, 'SizeData', 100);
grid on
hold on

p = polyfit(x, y, 1);

% Evaluate the polynomial at x values to get y values for the line of best fit
y_fit = polyval(p, x);

% Plot the line of best fit
fig1 = plot(x, y_fit, 'r-', 'LineWidth', 2);

title('Average Time Taken for a Search vs Number of Records in File')
set(gca,'FontSize',20)
set(fig1,'LineWidth',2)
xlabel('Number of Records')
ylabel('Average Search Time (s)')
xlim([0 1100])
ylim([0 12])