OPENQASM 3.0;
include "stdgates.inc";
bit[3] c0;
qubit[3] q1;
h q1[2];
cx q1[2], q1[1];
cx q1[0], q1[1];
h q1[0];
c0[0] = measure q1[0];
c0[1] = measure q1[1];
if (c0[1]) {
  x q1[2];
}
if (c0[0]) {
  z q1[2];
}
