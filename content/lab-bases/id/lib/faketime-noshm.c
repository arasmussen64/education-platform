/*
 * faketime-noshm: keeps libfaketime away from /dev/shm.
 *
 * libfaketime 0.9.10 (Ubuntu 24.04's) gives a machine its own clock in the
 * identity labs: lab-enter preloads it for every program started on a
 * machine that has an /etc/faketimerc. When it loads, the library wants a
 * named semaphore and a little shared memory in /dev/shm (its ft_shm_init
 * and ft_shm_create). The first program of a command makes them, named
 * after its process number, and puts the names in FAKETIME_SHARED; every
 * program started from there must open them, makes its own if it can't,
 * and exits with "sem_open failed and recreation attempts failed" if it
 * can do neither. On GitHub's runner that exit took every command on such
 * a machine ("Permission denied"), though it never happened on Docker
 * Desktop. The files are also never removed.
 *
 * All they do is let one command's processes agree on when the command
 * began, which a fixed offset read from a file doesn't need, and the
 * library is written to carry on without them: where it can't create its
 * semaphore it says nothing and shares nothing ("silently fail on
 * platforms that do not support sem_open()", in its source).
 *
 * So this is preloaded just before libfaketime, and answers the one call
 * that starts it all: sem_open for a name beginning "/faketime_sem_"
 * fails, as on a platform without named semaphores. No file is made,
 * FAKETIME_SHARED is never set, and no program is ever told to open
 * anything. Every other semaphore (Apache's modules make their own) goes
 * to the C library untouched.
 *
 * Built in the base's Dockerfile:
 *   gcc -O2 -fPIC -shared -o faketime-noshm.so faketime-noshm.c
 */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <errno.h>
#include <fcntl.h>
#include <semaphore.h>
#include <stdarg.h>
#include <string.h>
#include <sys/types.h>

sem_t *sem_open(const char *name, int oflag, ...)
{
  static sem_t *(*real)(const char *, int, ...);
  mode_t mode = 0;
  unsigned int value = 0;

  if (strncmp(name, "/faketime_sem_", 14) == 0)
  {
    errno = ENOSYS;
    return SEM_FAILED;
  }
  if (real == NULL)
  {
    real = (sem_t *(*)(const char *, int, ...)) dlsym(RTLD_NEXT, "sem_open");
    if (real == NULL)
    {
      errno = ENOSYS;
      return SEM_FAILED;
    }
  }
  /* The mode and the starting value are passed only when creating. */
  if (oflag & O_CREAT)
  {
    va_list args;
    va_start(args, oflag);
    mode = va_arg(args, mode_t);
    value = va_arg(args, unsigned int);
    va_end(args);
    return real(name, oflag, mode, value);
  }
  return real(name, oflag);
}
