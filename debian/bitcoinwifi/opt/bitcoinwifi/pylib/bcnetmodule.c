#include <arpa/inet.h>
#include <sys/socket.h>
#include <netdb.h>
#include <ifaddrs.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <netpacket/packet.h>
#include <net/ethernet.h>
#include <string.h>
#include <sys/ioctl.h>
#include <net/if.h>
#include <netinet/in.h>


#include <Python.h>

#define MACLEN 20 //Number of characters in a MAC address
static PyObject *BcnetError;

static PyObject *
bcnet_getnics(PyObject *self, PyObject *args)
{
    int sts=0;
	PyObject *nics = PyDict_New();
	sts = getnics(nics);
	if(sts){
		PyErr_SetString(BcnetError,
                sys_errlist[sts]);
        return NULL;
    };
    return nics;
}

static PyMethodDef BcnetMethods[] = {
    { "getnics", bcnet_getnics, METH_VARARGS, "Return a list of nics."},
    {NULL, NULL, 0, NULL} 
};

PyMODINIT_FUNC
initbcnet(void)
{
    PyObject *m;
    
    m = Py_InitModule("bcnet", BcnetMethods);
    if (m == NULL)
        return;

    BcnetError = PyErr_NewException("bcnet.error", NULL, NULL);
    Py_INCREF(BcnetError);
    PyModule_AddObject(m, "error", BcnetError);
}

int getnics(PyObject *nicDict) {
  
  char buf[8192] = {0};
  struct ifconf ifc = {0};
  struct ifreq *ifr = NULL;
  int sck = 0;
  int nInterfaces = 0;
  int i = 0;
  char ip[INET6_ADDRSTRLEN] = {0};
  char macp[MACLEN];
  struct ifreq *item;
  struct sockaddr *addr;
  PyObject *entry;
  
  sck = socket(PF_INET, SOCK_DGRAM, 0);
  if(sck < 0)
	  return errno;

  ifc.ifc_len = sizeof(buf);
  ifc.ifc_buf = buf;
  if(ioctl(sck, SIOCGIFCONF, &ifc) < 0)
    return errno;
  
  ifr = ifc.ifc_req;
  nInterfaces = ifc.ifc_len / sizeof(struct ifreq);

  for(i = 0; i < nInterfaces; i++)
  {
    item = &ifr[i];

    addr = &(item->ifr_addr);

    if(ioctl(sck, SIOCGIFADDR, item) < 0)
      return errno;

	if (inet_ntop(AF_INET, &(((struct sockaddr_in *)addr)->sin_addr), ip, sizeof ip) == NULL) //vracia adresu interf
        {
           strcpy(ip,"0.0.0.0");
           continue;
        }
    if(ioctl(sck, SIOCGIFHWADDR, item) < 0)
      return errno;

    sprintf(macp, "%02x:%02x:%02x:%02x:%02x:%02x",
    (unsigned char)item->ifr_hwaddr.sa_data[0],
    (unsigned char)item->ifr_hwaddr.sa_data[1],
    (unsigned char)item->ifr_hwaddr.sa_data[2],
    (unsigned char)item->ifr_hwaddr.sa_data[3],
    (unsigned char)item->ifr_hwaddr.sa_data[4],
    (unsigned char)item->ifr_hwaddr.sa_data[5]);
	
	entry = PyList_New(0);
	PyList_Append(entry, Py_BuildValue("s", macp));
	PyList_Append(entry, Py_BuildValue("s", ip));
	if(PyDict_SetItemString(nicDict, item->ifr_name,entry))
						return 1;
  }
  return 0;
}
