/**
 * @file mikegtr_HW02.c
 * @author Michael Gathara (mikegtr@uab.edu)
 * @date 2023-10-16
 *--------------------------Compilation--------------------------
 * @ManualCompile: gcc -o <name of exec> mikegtr_HW02.c
 * @ManualRun: ./<name of executable> -h
 * ---------------------------SUMMARY----------------------------
 * Print a file hierachy starting with the directory that is provided by the
 *command-line argument No arguments = start at current directory Print files
 *within a directory tabbed in Print symbolics links and what it points to
 * Arguments
 * -- -S, list everything
 * -- -s <file size in bytes>
 * -- -f <string pattern> <depth>
 */
#include <dirent.h>
#include <getopt.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>
#define BUFFSIZE 1024
int max_depth = -1;
int max_size = -1;
int show_details = 0;
char *search_str = NULL;
char *execute_command = NULL;
/**
 * @brief Get the mode string object
 *
 * @param mode
 * @param buf
 */
void get_mode_string(mode_t mode, char *buf) {
    const char chars[] = "rwxrwxrwx";
    for (size_t i = 0; i < 9; i++) {
        buf[i] = (mode & (1 << (8 - i))) ? chars[i] : '-';
    }
    buf[9] = '\0';
}
/**
 * @brief Prints a file hierachy starting with the directory that is provided by
 * the command-line argument
 *
 * @param name, the name of the dir to start at
 * @param depth, how deep to go
 */
void search_dir(const char *name, int depth) {
    DIR *dir;
    struct dirent *entry;
    struct stat st;
    int flag;
    if (!(dir = opendir(name))) return;
    if ((entry = readdir(dir)) == NULL) return;
    do {
        flag = 1;
        if (entry->d_type == DT_DIR) {
            char path[1024];
            if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0)
                continue;
            printf("\n");
            snprintf(path, sizeof(path), "%s/%s", name, entry->d_name);
            printf("%*s[%s]\n", depth * 2, "", entry->d_name);
            if (max_depth == -1 || depth < max_depth)
                search_dir(path, depth + 1);
        } else if (entry->d_type == DT_REG) {
            char path[1024];
            int count = 0;
            snprintf(path, sizeof(path), "%s/%s", name, entry->d_name);
            stat(path, &st);
            int flag = 1;

            if (max_size != -1 && st.st_size > max_size) {
                flag = 0;
            }
            if (search_str != NULL && !strstr(entry->d_name, search_str))
                flag = 0;
            }
            

            // This seems to work, but are you making sure to run the command on each file rather than just running the command?
            if (execute_command) {
                pid_t pid = fork();  // Create a child process

                if (pid == 0)  // This is the child process
                {
                    // Execute the command using /bin/sh -c
                    execlp("/bin/sh", "/bin/sh", "-c", execute_command,
                           (char *)NULL);

                    // If execvp fails, print an error message
                    perror("execvl");
                    exit(EXIT_FAILURE);  // Exit the child process

                } else if (pid < 0)  // Fork failed
                {
                    perror("fork");
                    exit(EXIT_FAILURE);
                } else  // This is the parent process
                {
                    int status;
                    wait(&status);  // Wait for the child process to finish
                    if (WIFEXITED(status) && WEXITSTATUS(status) != 0) {
                        // Handle non-zero exit code from child if needed
                    }
                }

                flag = 0;
            }

            // if (execute_command) {
            //     pid_t pid = fork();  // Create a child process

            //     if (pid == 0)  // This is the child process
            //     {
            //         // Execute the command specified after the '-e' flag

            //         // Execute the command using /bin/sh -c
            //         execlp("/bin/sh", "/bin/sh", "-c", execute_command,
            //                (char *)NULL);

            //         // If execvp fails, print an error message
            //         perror("execvl");
            //         exit(EXIT_FAILURE);  // Exit the child process
            //         flag = 0;

            //     } else if (pid < 0)  // Fork failed
            //     {
            //         perror("fork");
            //         exit(EXIT_FAILURE);
            //     } else  // This is the parent process
            //     {
            //         wait(NULL);  // Wait for the child process to finish
            //         exit(EXIT_SUCCESS);
            //     }
            //     flag = 0;
            // }

            if (flag) {
                if (show_details) {
                    char mode[10];
                    get_mode_string(st.st_mode, mode);
                    char timebuf[128];
                    strftime(timebuf, sizeof(timebuf), "%Y-%m-%d %H:%M:%S",
                             localtime(&st.st_atime));
                    printf("%*s%-10s %-10ld %-20s %-20s\n", depth * 2, "", mode,
                           st.st_size, timebuf, entry->d_name);
                }

                else {
                    printf("%*s%-10ld %-20s\n", depth * 2, "", st.st_size,
                           entry->d_name);
                }
            }
        }

    while ((entry = readdir(dir)) != NULL);
    closedir(dir);
}

int main(int argc, char **argv) {
    int opt;
    char *dir = ".";
    /**
     * if you want to be able to do long options
     * -s 1024 can be --size=1024
     * etc
     */
    static struct option long_options[] = {
        {"size", required_argument, 0, 's'},
        {"find", required_argument, 0, 'f'},
        {"execute", required_argument, 0, 'e'},
        {0, 0, 0, 0}};
    int long_index = 0;
    while ((opt = getopt_long(argc, argv, "Ss:f:e:", long_options,
                              &long_index)) != -1) {
        switch (opt) {
            case 's':
                max_size = atoi(optarg);
                break;
            case 'f':
                search_str = optarg;
                if (optind < argc && argv[optind][0] != '-') {
                    max_depth = atoi(argv[optind]);
                    optind++;
                }
                break;
            case 'S':
                show_details = 1;
                break;

            case 'e':
                execute_command = optarg;
                // printf("%s",optarg);
                break;

            default:
                break;
        }
    }
    if (optind < argc) {
        dir = argv[optind];
    }
    search_dir(dir, 0);
    return 0;
}
// int main(int argc, char **argv) {
// int i;
// char *dir = ".";
// // As this is a bare bones version of Homework 2. I just used a for loop,
// feel free to change this to getopt if you'd like for (i = 1; i < argc;
// i++) {
// if (argv[i][0] == '-') {
// if (strcmp(argv[i], "-s") == 0) max_size = atoi(argv[++i]);
// else if (argv[i][1] == 'f') search_str = argv[++i]; max_depth =
// atoi(argv[++i]);
// } else {
// dir = argv[i];
// }
// }
// search_dir(dir, 0);
// return 0;
// }
