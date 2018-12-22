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
  if (argc < 2 || argc > 7) {
    printf("mksub-ts [stubs/xit] [xits] [xit_nodes] [xit_p] [stub_nodes] [stub_p]\n");
    exit(1);
  }

  int a = atoi(argv[1]);
  int b = atoi(argv[2]);
  int c = atoi(argv[3]);
  double d = strtod(argv[4], NULL);
  int e = atoi(argv[5]);
  double f = strtod(argv[6], NULL);
    
  FILE * fp;
  FILE * reqfile;
  char filename[LEN_FILENAME], reqfilename[LEN_FILENAME];
  char cmd[LEN_CMD];
  int *n_x, *n_y, t1, t2;
  
  int num_nodes, num_edges, from, to;

  sprintf(filename, "itm-specsub-ts");
  fp = fopen(filename, "w");

  fprintf(fp, "ts 1 47\n"); // generate one substrate graph
  fprintf(fp, "%d 20 20\n", a);
  fprintf(fp, "%d 2 3 1.0\n", b);
  fprintf(fp, "%d 5 3 %.1f\n", c, d);
  fprintf(fp, "%d 5 3 %.1f\n", e, f);

  fclose(fp);

  sprintf(cmd, "itm itm-specsub-ts");
  printf("%s\n", cmd);
  system(cmd);

  sprintf(cmd, "sgb2alt itm-specsub-ts-0.gb sub-ts.alt");
  printf("%s\n", cmd);
  system(cmd);
   
  char str[1000];
  int j;
  sprintf(filename, "sub-ts.alt");
  fp = fopen(filename, "r");
  sprintf(reqfilename, "sub-ts.txt");
  reqfile = fopen(reqfilename, "w");

  // remove preamble
  for (j = 0; j < 10; j ++)
    fscanf(fp, "%s", str);

  fscanf(fp, "%d %d %*d %*d", &num_nodes, &num_edges);

  num_edges /= 2;

  fprintf(reqfile, "%d %d\n", num_nodes, num_edges);

  for (j = 0; j < 14; j ++) {
    fscanf(fp, "%s", str);
    //printf("%s\n", str);
  }

  n_x = (int *)malloc(num_nodes * sizeof(int));
  n_y = (int *)malloc(num_nodes * sizeof(int));

  // generate CPU resources resources for the nodes
  for (j = 0; j < num_nodes; j ++) {
    fscanf(fp, "%d %s %d %d", &t1, str, &n_x[j], &n_y[j]);
    //printf("%d %d %d %d\n", t1, t2, n_x[j], n_y[j]);
    if(j < 4)
       fprintf(reqfile, "%d %d %lf\n", n_x[j], n_y[j], 200 + (rand()/(double)RAND_MAX +1.) * (double)MAX_CPU * 0.5);
    else
       fprintf(reqfile, "%d %d %lf\n", n_x[j], n_y[j], (rand()/(double)RAND_MAX +1.) * (double)MAX_CPU * 0.5);
  }
  
  for (j = 0; j < 6; j ++) {
    fscanf(fp, "%s", str);
    //printf("%s\n", str);
  }       

  // generate bandwidth for the links
  for (j = 0; j < num_edges; j ++) {
    fscanf(fp, "%d %d %*d %*d", &from, &to);
    if(from < 4 && to < 4)
       fprintf(reqfile, "%d %d %lf %lf\n", from, to, 200 + (rand()/(double)RAND_MAX +1.) * (double)MAX_BW * 0.5, dis(n_x[from], n_y[from], n_x[to], n_y[to]));
    else if(from < 4 || to < 4)
        fprintf(reqfile, "%d %d %lf %lf\n", from, to, 100 + (rand()/(double)RAND_MAX +1.) * (double)MAX_BW * 0.5, dis(n_x[from], n_y[from], n_x[to], n_y[to]));
    else
       fprintf(reqfile, "%d %d %lf %lf\n", from, to, (rand()/(double)RAND_MAX +1.) * (double)MAX_BW * 0.5, dis(n_x[from], n_y[from], n_x[to], n_y[to]));
  }

  free(n_x);
  free(n_y);

  fclose(fp);
  fclose(reqfile);

  return 0;
}

