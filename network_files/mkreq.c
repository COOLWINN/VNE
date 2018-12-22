#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <math.h>
#include <time.h>

#include "def.h"

#define POISSON_MEAN 40
#define TOTAL_TIME 50000

#define REQ_DURATION        1000
#define MIN_REQ_DURATION    250

#define MIN_NUM_NODE    3
#define LARGE_NUM_NODE   20

double dis(int x1, int y1, int x2, int y2) {
  return sqrt((x1-x2)*(x1-x2)+(y1-y2)*(y1-y2));
}

int poisson(double lambda) {
  double p;
  int r;
  p = 0;
  r = 0;

  while (1) {
    p = p - log(rand() / (double)RAND_MAX);
    if (p < lambda) {
      r++;
    } else {
      break;
    }
  }
  
  return r;
}

int main(int argc, char **argv) {
  int xseed = (unsigned)time(NULL);  // Current Time
  srand( xseed ); 

  if (argc != 5) {
    printf("mkreq <n> <link_r> <cpu_r>\n");
    exit(1);
  }

  int n = atoi(argv[1]);  // number of graphs
  double link_rate = atoi(argv[2])/(double)100;  // bound max bw
  double cpu_rate = atoi(argv[3])/(double)100;  // bound max cpu
  int MAX_DISTANCE = 20;
  int scale = 100;

  FILE * fp;
  FILE * reqfile;
  char filename[LEN_FILENAME], reqfilename[LEN_FILENAME];
  char cmd[LEN_CMD];
  int i, k = 0, countk = 0, p = 0, start;
  int *n_x, *n_y, t1, t2;
  int l_c = 0, a_c = 0;
  
  int num_nodes, num_edges, split, time, duration, from, to, maxD = MAX_DISTANCE, avg = LARGE_NUM_NODE / 2;

  for (i = 0; i < n; i ++) {
    sprintf(filename, "spec/itm-spec%d", i);
    fp = fopen(filename, "w");
    fprintf(fp, "geo 1\n");
    int t;

    int ran = rand();
    t = (rand() % (LARGE_NUM_NODE - MIN_NUM_NODE)) + MIN_NUM_NODE;
    fprintf(fp, "%d %d 2 0.5 0.2\n", t, scale); // scale: 50; method: 2; alpha: 0.5; beta: 0.2; gamma: default
    fclose(fp);
  }

  sleep(1);

  for (i = 0; i < n; i ++) {
    sprintf(cmd, "itm spec/itm-spec%d",i);
    //printf("%s\n", cmd);
    system(cmd);
  }

  for (i = 0; i < n; i ++) {
    sprintf(cmd, "sgb2alt spec/itm-spec%d-0.gb alt/%d.alt", i, i);
    //printf("%s\n", cmd);
    system(cmd);
  }
   
  char str[1000];
  int j;
  for (i = 0; i < n; i ++) {
    printf("generate req %d\n", i);
    sprintf(filename, "alt/%d.alt", i);
    fp = fopen(filename, "r");
    sprintf(reqfilename, "requests/req%d.txt", i);
    reqfile = fopen(reqfilename, "w");
    if (reqfile == NULL) {
      printf("couldn't open file %s\n", reqfilename);
      exit(1);
    }

    for (j = 0; j < 10; j ++)
      fscanf(fp, "%s", str);

    fscanf(fp, "%d %d %*d %*d", &num_nodes, &num_edges);
    num_edges /= 2;

    if (countk == k) {
      k = 0;
      while( k == 0) {
        k = poisson(POISSON_MEAN);
      }
      countk = 0;
      printf("k %d\n", k);
      start = (p * TOTAL_TIME * POISSON_MEAN) / n;
      p++; 
    }

    time = start + ((countk + 1) * TOTAL_TIME * POISSON_MEAN) / (n * (k + 1));
    countk ++;

    duration = MIN_REQ_DURATION + (int)(-log(rand() / (double)RAND_MAX) * (REQ_DURATION - MIN_REQ_DURATION)); // exponentially distributed duration

    fprintf(reqfile, "%d %d %d %d %d\n", num_nodes, num_edges, time, duration, maxD);
    printf("nodes %d, edges %d\n", num_nodes, num_edges);
    printf("time %d, duration %d\n", time, duration);

    // skip
    for (j = 0; j < 11; j ++) {
      fscanf(fp, "%s", str);
      //printf("%s\n", str);
    }

    n_x = (int *)malloc(num_nodes * sizeof(int));
    n_y = (int *)malloc(num_nodes * sizeof(int));

    /* alloc CPU resources for eache virtual node */
    for (j = 0; j < num_nodes; j ++) {
      fscanf(fp, "%d %d %d %d", &t1, &t2, &n_x[j], &n_y[j]);
      //printf("%d %d %d %d\n", t1, t2, n_x[j], n_y[j]);      
      //double t = rand();
      fprintf(reqfile, "%d %d %lf\n", n_x[j], n_y[j],rand() / (double)RAND_MAX * (double)MAX_CPU * cpu_rate);
    }
    
    // skip
    for (j = 0; j < 6; j ++) {
      fscanf(fp, "%s", str);
      //printf("%s\n", str);
    }       
    /* alloc bandwidth for eache virtual link */
    for (j = 0; j < num_edges; j ++) {
      fscanf(fp, "%d %d %*d %*d", &from, &to);
        fprintf(reqfile, "%d %d %lf %lf\n", from, to, rand()/(double)RAND_MAX * (double)MAX_BW * link_rate, (1. + rand()/(double)RAND_MAX) * dis(n_x[from], n_y[from], n_x[to], n_y[to])); 
    }

    free(n_x);
    free(n_y);

    fclose(fp);
    fclose(reqfile);
  }
  
  return 0;
}

