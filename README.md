# Course-Scheduler

My Final project for the **Linear Optimization** course at **Amirkabir University of Technology**.

# Requirements

- pandas
- openpyxl
- pulp

# Problem Formulation

| Counter | Counts |
| :---: | :---: |
| $i$ | Teachers |
| $j$ | Classes |
| $k$ | Days |
| $t$ | Teachers' Availability periods |

| Variable | Definition |
| :---: | :---: |
| $X_{i,j}$ | Teacher $i$ has class $j$ |
| $D_{i,j,k}$ | Teacher $i$ has class $j$ on day $k$ |
| $S_{i,j,k,t}$ | Teacher $i$ has class $j$ on day $k$ and availability period $t$ |
| $B_j$ | Start of the period eligible to begin class $j$ |
| $E_j$ | End of the period eligible to begin class $j$ |

| Constant | Definition |
| :---: | :---: |
| $c_i$ | Knowledge level of teacher $i$ |
| $l_i$ | Teacher $i$'s salary per class |
| $m_i$ | Maximum classes teacher $i$ can teach |
| $b_{i,k,t}$ | Start hour of teacher $i$'s availability period $t$ on day $k$ |
| $e_{i,k,t}$ | End hour of teacher $i$'s availability period $t$ on day $k$ |
| $f_j$ | Fee to sign up for class $j$ |
| $a_j$ | Number of students in class $j$ |
| $n_j$ | Number of sessions of class $j$ per week |
| $c'_{j}$ | Required knowledge level to teach class $j$ |

### Objective Function:

$`Max \;\, z = \displaystyle \sum_{i \in Teachers} \sum_{j \in Classes} f_j a_j X_{i,j} - \displaystyle \sum_{i \in Teachers} \sum_{j \in Classes} l_i X_{i,j} - \displaystyle \sum_{i \in Teachers} \frac{1500 \times 1.5 \times \sum_{j \in Classes} \sum_{k \in Days} D_{i,j,k}}{44 \times 52}`$

The objective function maximizes profit by summing assigned class fees, subtracting teacher salaries and insurance costs.

### Constraints:
1. Each class has at most one teacher: <br/> 
   $\forall j \in Classes: \displaystyle \sum_{i \in Teachers} X_{i,j} \leq 1$

2. Weekly class sessions match the class session constant: <br/> 
   $`\forall j \in Classes \;\; \forall i \in Teachers : \displaystyle \sum_{k \in Days} S_{i,j,k} = X_{i,j} a_j`$

3. If a day is reserved for class $j$ by teacher $i$, exactly one availability period includes the class: <br/>
   $`\forall j \in Classes \;\; \forall i \in Teachers \;\; \forall k \in Days: \displaystyle \sum_{t \in Periods} S_{i,j,k,t} = D_{i,j,k}`$

4. Reserved availability period starts before the class starts: <br/>
   $`\forall j \in Classes \;\; \forall i \in Teachers \;\; \forall k \in Days \;\; \forall t \in Periods: S_{i,j,k,t} b_{i,k,t} \leq B_j`$

5. Reserved availability period ends after the class ends: <br/>
   $`\forall j \in Classes \;\; \forall i \in Teachers \;\; \forall k \in Days \;\; \forall t \in Periods: S_{i,j,k,t} e_{i,k,t} + 24(1-S_{i,j,k,t}) \geq E_j + 1.5`$

6. Teacher meets required class knowledge level: <br/>
   $\forall j \in Classes : \displaystyle \sum_{i \in Teachers} c_i X_{i,j} \geq c'_j$

7. Classes taught by a professor don't exceed their maximum: <br/>
   $\forall i \in Teachers: \displaystyle \sum_{j \in Classes} X_{i,j} \leq m_i$

8. Variables are nonnegative; decision variables are binary: <br/>
   $`\begin{cases}
   \text{All variables} \geq 0 \\
   X_{i,j}, D_{i,j,k}, S_{i,j,k,t} \in \{0, 1\}
   \end{cases}`$



# Implementation Details

1. Constants are read from `Data.xlsx`; the number of teachers, classes, and availability periods can be adjusted.

2. To address potential infeasibility, a `Cancel` flag is added to the teacher list, indicating class cancellation. This teacher has the highest knowledge level and zero salary, with no class fees or insurance added to the objective function.

3. The code outputs a range $(B_j, E_j)$ for each class, allowing flexible class start times within this period.

# Sample Output

```bash
Total Number of Variables : 4117
Total Number of Constraints : 6601
--------------------------------------------------
Total Calculation Time : 1.218323496002995
Model's Result : Optimal
--------------------------------------------------
z* = 42283.94667832188
--------------------------------------------------
Print optimal value for all variables? (y,n) n
--------------------------------------------------
Print human readable solution? (y,n) n
--------------------------------------------------
Press any key to exit...
```

# Limitations

- For efficiency and to reduce variables and constraints, no check ensures sufficient time for courses within an availability period. This can be addressed by iteratively filling desired availability periods with class sessions and rerunning the program.