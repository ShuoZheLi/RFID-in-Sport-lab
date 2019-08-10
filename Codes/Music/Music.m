%MUSIC for Uniform Linear Array%
clear; close all;
derad = pi/180;
Number_Antenna = 20;               %Number of Antenna        
Signal_Source = 4;               %Number of Signal Source
Incident_Angle = [-60 -30 0 30];  %Incident Angles
Signal_to_Noise_ratio = 10;            %Gaussian Signal to Noise ratio
Number_Of_Sample = 1000;             %Number of Sample
 
Distance_Antenna = 0.5;            %Distance between antennas 
d=0:Distance_Antenna:(Number_Antenna-1)*Distance_Antenna;
Steering_Matrix=exp(-1i*2*pi*d.'*sin(Incident_Angle*derad));
% Modeling the Signals
S=randn(Signal_Source,Number_Of_Sample); 
X=Steering_Matrix*S;
%Add Gaussian noise
X1=awgn(X,Signal_to_Noise_ratio,'measured');
%Calculate the covariance matrix
Rxx=X1*X1'/Number_Of_Sample;
%Evigenvalue decomposition
[EV,D]=eig(Rxx);
EVA=diag(D)';
[EVA,I]=sort(EVA);
EV=fliplr(EV(:,I));
Evigen_Space=EV(:,Signal_Source+1:Number_Antenna);

%Calculate the spatial power spectrum of every angle
for angles = 1:361
    angle(angles)=(angles-181)/2;
    phim=derad*angle(angles);
    a=exp(-1i*2*pi*d*sin(phim)).';    
    Spatial_Power_Spectrum(angles)=1/(a'*Evigen_Space*Evigen_Space'*a);
end
Spatial_Power_Spectrum=abs(Spatial_Power_Spectrum);
Spatial_Power_Spectrum=10*log10(Spatial_Power_Spectrum);
h=plot(angle,Spatial_Power_Spectrum);
set(h,'Linewidth',0.5);
xlabel('Incident Angle(degree)');
ylabel('Spatial Power Spectrum(dB)');
set(gca, 'XTick',[-90:30:90]);
grid on;
