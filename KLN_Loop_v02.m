function [output, Nodes] = KLN_Loop_v02(A,L,itt)

%% A is a given
%% L is lamda (as in resolution parameter)
%% itt is the number of times you want to go from random starting 's' to
%% KLN completion.

%% TRII 08/01/09

%% Set up initial variables, holders of values
n=length(A);
Nodes(:,1)=1:n;

%% Just some parameters to make modifying the code easier
span_space_mod=0.55;
s_type='ran';
count=1;

%% Start recursive unit finder
while length(unique(Nodes(:,count)))>1
    
    %% Some initial variables ('A' changes with each iteration, so it's
    %% necessary to update 'n').
    n=length(A);
    s_start_hold=zeros(n,itt);
    s_final_hold=zeros(n,itt);
    
    %% Run mKL itt number of times
    for ji=1:itt
        switch s_type
            case 'ran'
            s=span_space(n,n*span_space_mod);
            case 'one'
            s=ones(size(s));
        end
        s_start_hold(:,ji)=s;
        [s,Q,time] = newmankl_allownew(s,A,1:n,L);
        s=reass_groups(s);
        s_final_hold(:,ji)=s';
        Q_hold(:,ji)=[Q;time];
    end

    %% Find only those partitions which are unique out of the itt found
    %% using unique is probably better...
    same_partition_list = compare_partitions(s_final_hold,Q_hold(1,:));
    for ji=1:length(same_partition_list)
        unique_partition_indx(ji)=same_partition_list{ji}(1);
    end
    
    groups_final=max(s_final_hold(:,unique_partition_indx),[],1);
    Q_hold=[Q_hold(unique_partition_indx)' groups_final']';

    %% Re-package variables to make nicer for export
    s_Store.s_final_hold=s_final_hold;
    s_Store.Q=Q_hold;
    s_Store.upi=unique_partition_indx;
    s_Store.spl=same_partition_list;

    %% Begin units stuff
    Units=Unit_Finder(s_final_hold(:,unique_partition_indx));
    Unit_Stat = U3(Units,s_final_hold(:,unique_partition_indx));
    [U_A_O U_A_I] = Cre8_Unit_A(Units,A);

    %% Again, repackage
    U_Store.Units=Units;
    U_Store.Unit_Stat=Unit_Stat;
    U_Store.A=U_A_O;
    U_Store.W=U_A_I;
    
    %% Place new units in Nodes and rearrange previous nodes
    [Nodes(:,count:count+1) indx] = Units2Nodes(Units,Nodes(:,count));
    Nodes(:,1:count-1)=Nodes(indx,1:count-1);
    
    %% Package into the output storage
    output{1,count}=s_Store;
    output{2,count}=U_Store;
    output{3,count}=indx;
    
    %% Assign new A
    A=U_A_O;
    count=count+1;
    
end

%%----------------------------------------------

function s = span_space(g,max_g);

max_g=round(max_g);
group_num = ceil(rand(1,1)*max_g);
left_over=mod(g, group_num);
for i = 1:(g-left_over)/group_num
    s((i-1)*group_num+1:i*group_num)=randperm(group_num);
end
for i = 1:left_over
    s(g-i+1)=ceil(group_num*rand(1,1));
end

%%----------------------------------------------

function [groups,Q,time,numiter] = newmankl_allownew(groups,A,indx,L)

% 'L' is the resolution parameter.  max value is when
% A{i,j}max-L*k{i}*k{j}/(2*m) = 0;
% if no index is specified, assume all in A
if (nargin<3),indx=1:length(A);end  
if (size(indx,1)>size(indx,2)),indx=indx';end
% if no resolution paramater assigned, assume unity
if (nargin<4),L=1;end

%Identify distinct group values and number of cut levels in dendrogram:
groupnumbers=unique(groups);
differences=diff(groupnumbers);
cuts=length(unique(differences));

%Identify partitions to iterate with:
gpart=unique(groups(indx));

%Some basics about the network:
N=length(A);
k=full(sum(A,2));
kk2m=k.^2/sum(k)*L;

%Initial modularity:
Q=modularity(groups,A,L);
indxorig=indx;
numiter=0;
Q0=-999;
%Iterations:
tic;
while (Q>Q0), %Outer loop until improvement not found inside
    %disp([int2str(numiter),':  Q = ',num2str(Q),...
    %    ' for ',int2str(length(unique(groups))),' communities'])
    Q0=Q;
    numiter=numiter+1;
    indx=indxorig;
    gpart=unique(groups(indx));
    testgroups=groups;
    while ~isempty(indx), %Move each node precisely once
        nodecontributions=zeros(length(A),length(gpart));
        for ig=1:length(gpart),
            nodecontributions(:,ig)=...
                BMultiply((testgroups==gpart(ig))',A,1:length(A),L);
        end
        glookup(gpart)=1:length(gpart);
        currcontribindex=[1:N]'+(glookup(testgroups)'-1)*N;
        currcontrib=nodecontributions(currcontribindex)+kk2m;
        nodecontributions=nodecontributions-...
            currcontrib*ones(1,length(gpart));
        nodecontributions(currcontribindex)=-999; %Ignore current placement
        nodecontributions=nodecontributions(indx,:); %Restrict to available nodes
        currcontrib=currcontrib(indx,:); %Restrict to available nodes
        maxvalue=max(max(nodecontributions)); %Identify best available switch
        [i,g]=find(nodecontributions==maxvalue);
        ii=ceil(length(i)*rand(1)); %break ties randomly
        besti=indx(i(ii)); 
	bestg=gpart(g(ii));
        makenew=find(-currcontrib(i)>=maxvalue);%if current placement 
        %better than or equal to placement in another existing group, 
        %move to its own group
        if ~isempty(makenew), %break ties by moving available to new
            maxmakenew=max(-currcontrib(i(makenew)));
            mmnew=find(-currcontrib(i(makenew))==maxmakenew);
            try
                besti=indx(i(makenew(mmnew(ceil(length(mmnew)*rand(1))))));
            catch
                keyboard
            end
            bestg=max(testgroups)+1;
            gpart=[gpart,bestg];
        end
        testgroups(besti)=bestg; %move node i to new group
        indx(find(indx==besti))=[]; %remove i from indx list of nodes to be moved
        bestQ=modularity(testgroups,A,L); %calculate Q
        if (bestQ>Q), %Keep track of configuration with highest Q.
            groups=testgroups;
            Q=bestQ;
        end
    end
end
time=toc;
%disp([int2str(numiter),':  Stopped because bestQ = ',num2str(bestQ)])
Q=modularity(groups,A,L);

%----------------------------%
function Q = modularity(g,A,L)
numcomms=max(g);
Q=0;
indx=1:length(A);
for ic=1:numcomms,
    x=(g==ic);
    Q=Q+x*BMultiply(x',A,indx,L);
end
Q=Q/sum(sum(A));

%----------------------------%
function v = BMultiply(x,A,indx,L)
j=full(sum(A,2)); %j is a column vector
jx=j'*x; %jx is the dot product of j and x
twom=sum(j);
jx=full(jx);
x2=(A*x);
x3=(L*jx/twom)*j;
v=x2-x3;
v=v(indx);

%%----------------------------------------------

function groups = reass_groups(groups)

% reassigns group numbers so that the maximum group number corresponds to
% the number of groups, and the first node is in the first groups, etc.
groups_nums = unique(groups);
num_groups = length(groups_nums);
groups=groups+groups_nums(end);
groups_nums=groups_nums+groups_nums(end);

pos_index=zeros(1,num_groups);
for index = 1:num_groups
    pos_index(index)=...
        find(groups==groups_nums(index),1);
end
pos_index=sort(pos_index,'ascend');
for index = 1:num_groups
    groups(groups==groups(pos_index(index))) = index;
end

%%----------------------------------------------

%% This function is designed to compare various partitions from a
%% particular run of KLN_Loop in order to see how many hits each partition
%% type has received.

function same_partition_list = compare_partitions(groups,Q)

%% Assigne initial variables
[N itt]=size(groups);
index=1:itt;
same_partition_list=cell(0);
while ~isempty(index)
    %% Find other partitions with same Q as current partition
    temp_compare=find(Q<Q(index(1))+1e-8 & Q>Q(index(1))-1e-8);
    temp_same_partition_list=temp_compare(1);
    temp_compare(1)=[];
    %% Further testing needed if modularities are equal..
    if ~isempty(temp_compare)
        %% Get stats on current partition
        ref_groups=unique(groups(:,index(1)));
        for ii=1:length(ref_groups)
            sizes(ii)=length(find(groups(:,index(1))==...
                ref_groups(ii)));
        end
        %% New addition...quicker than below...
        for jj=1:length(temp_compare)
            if sum(groups(:,jj)-groups(:,index(1)))==0
                temp_same_partition_list=...
                   [temp_same_partition_list temp_compare(jj)];
                index(index==temp_compare(jj))=[];
            else
            %% Compare stats on other partitions if there are other partitions
            %% with the same Q
                temp_groups=...
                    unique(groups(:,temp_compare(jj)));
                if temp_groups(end)==ref_groups(end)
                    for ii=1:length(ref_groups)
                        temp_sizes(ii)=length(find...
                            (groups(:,temp_compare(jj))==...
                        temp_groups(ii)));
                    end
                    for ii=1:length(ref_groups)
                        test=find(temp_sizes==sizes(ii),1);
                        if isempty(test),break
                        else, temp_sizes(test)=[];
                        end
                    end
                    if isempty(temp_sizes)
                        temp_same_partition_list=...
                            [temp_same_partition_list temp_compare(jj)];
                        index(index==temp_compare(jj))=[];
                    else,temp_sizes=[];
                    end
                end
                temp_groups=[];
            end
        end
    end
    index(1)=[];
    same_partition_list{end+1}=temp_same_partition_list;
end

%%----------------------------------------------

%% Determines which sets of nodes, if any, are always placed together for
%% the various partitions encountered 

function Units = Unit_Finder(groups_all)

[node_number, n] = size(groups_all);
groups_count = 1;
Units = zeros(node_number,1);
index = 1:node_number;
contintue = 1;
while contintue == 1
    x = find(Units == 0, 1);
    Units(x) = groups_count;
    index(index == x) = [];
    index_mod = [];
    for ii = index
        % checking to see for how many trials two nodes are placed in
        % the same community
        % threshold for how many times two nodes need to appear together in
        % communities to be in the same unit; all the time is the only
        % measure that makes sense at the moment
        if (sum(groups_all(ii,:) == groups_all(x,:))) >= n
            Units(ii) = Units(x);
            index_mod = [index_mod ii];
        end
    end
    for i = 1:length(index_mod)
        index(index == index_mod(i)) = [];
    end
    groups_count = groups_count + 1;
    if isempty(index)
        contintue = 0;
    end
end

%%----------------------------------------------

function Unit_Stat = U3(Units,groups_all);

[Unit_Num nodes J] = unique(Units);
%% [B I J] = unique(A)
% B=A(I); A=B(J);
num=length(nodes);
Unit_Stat=sparse(num,num);
t=size(groups_all,2);

for i=1:num-1
    for ii=i+1:num
        Unit_Stat(i,ii)=...
            sum(groups_all(nodes(i),:)==groups_all(nodes(ii),:))/t;
    end
end

%%----------------------------------------------

%% Condenses nodes into meta-nodes based on units as found by KLN.  An A
%% matrix is then created for these meta-nodes, for which connection
%% weights are the sum of connection weights between nodes in the
%% corresponding two units in question.  This is U_A_O.  U_A_I is the total
%% connection weight of internal connections within a unit.
%% 23/01/09 TRII

function [U_A_O U_A_I] = Cre8_Unit_A(Units,A);

%% Get size, create U_A
[Unit_Num nodes J] = unique(Units);
U=length(nodes);
U_A_O=sparse(U,U);
U_A_I=zeros(U,1);

%% Create array with the node numbers that are members of each unit
for i=1:U
    Units_Store{i}=find(Units==Unit_Num(i));
end

%% Find values for U_A_O, U_A_I
for i=1:U-1
    for ii=i+1:U
        U_A_O(i,ii)=...
            sum(sum(A(Units_Store{i},Units_Store{ii})));
    end
    U_A_I(i)=sum(sum(A(Units_Store{i},Units_Store{i})));
end
% Make A symmetric
U_A_O=U_A_O+U_A_O';

%%----------------------------------------------

%% This function links nodes to units or units to meta-units 

function [Nodes indx] = Units2Nodes(Units,Nodes)

for i=1:length(Units)
    Nodes(Nodes(:,1)==i,2)=Units(i);
end

[Nodes(:,2) indx] = sort(Nodes(:,2));
Nodes(:,1)=Nodes(indx,1);