#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <math.h>
#include <time.h>

#include "def.h"

double dis(int x1, int y1, int x2, int y2) {
  return sqrt((x1-x2)*(x1-x2)+(y1-y2)*(y1-y2));
}

int main(int argc, char **argv) {

  srand(time(NULL));
  if (argc != 2 && argc != 3) {
	  printf("mksub n [p]\n");
    exit(1);
  }

  int n = atoi(argv[1]);
  int scale = 100;

  double p = 0.5;
  if(argc == 3)
	  p = strtod(argv[2], NULL);
    
  FILE * fp;
  FILE * reqfile;
  char filename[LEN_FILENAME], reqfilename[LEN_FILENAME];
  char cmd[LEN_CMD];
  int *n_x, *n_y, t1, t2;
  
  int num_nodes, num_edges, from, to;

  sprintf(filename, "itm-specsub");
  fp = fopen(filename, "w");
  
  // generate one substrate graph
  fprintf(fp, "geo 1\n"); 
  // scale: 100; method: 2; alpha: 0.5; beta: 0.2; gamma: default
  fprintf(fp, "%d %d 2 %.1f 0.2\n", n, scale, p); 
    
  fclose(fp);

  sleep(1);

  sprintf(cmd, "itm itm-specsub");
  printf("%s\n", cmd);
  system(cmd);

  sprintf(cmd, "sgb2alt itm-specsub-0.gb sub.alt");
  printf("%s\n", cmd);
  system(cmd);
   
  char str[1000];
  int j;
  sprintf(filename, "sub.alt");
  fp = fopen(filename, "r");
  sprintf(reqfilename, "sub.txt");
  reqfile = fopen(reqfilename, "w");

  // remove preamble
  for (j = 0; j < 10; j ++)
    fscanf(fp, "%s", str);

  fscanf(fp, "%d %d %*d %*d", &num_nodes, &num_edges);

  num_edges /= 2;

  fprintf(reqfile, "%d %d\n", num_nodes, num_edges);

  for (j = 0; j < 11; j ++) {
    fscanf(fp, "%s", str);
    //printf("%s\n", str);
  }

  n_x = (int *)malloc(num_nodes * sizeof(int));
  n_y = (int *)malloc(num_nodes * sizeof(int));

  // generate CPU resources resources for the nodes
  for (j = 0; j < num_nodes; j ++) {
    fscanf(fp, "%d %d %d %d", &t1, &t2, &n_x[j], &n_y[j]);
    //printf("%d %d %d %d\n", t1, t2, n_x[j], n_y[j]);
    fprintf(reqfile, "%d %d %lf\n", n_x[j], n_y[j], (rand()/(double)RAND_MAX +1.) * (double)MAX_CPU * 0.5);
  }
  
  for (j = 0; j < 6; j ++) {
    fscanf(fp, "%s", str);
    //printf("%s\n", str);
  }       

  // generate bandwidth for the links
  for (j = 0; j < num_edges; j ++) {
    fscanf(fp, "%d %d %*d %*d", &from, &to);
    fprintf(reqfile, "%d %d %lf %lf\n", from, to, (rand()/(double)RAND_MAX +1.) * (double)MAX_BW * 0.5, dis(n_x[from], n_y[from], n_x[to], n_y[to])); 
  }

  free(n_x);
  free(n_y);

  fclose(fp);
  fclose(reqfile);

  return 0;
}

