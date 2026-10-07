OPENQASM 2.0;
include "qelib1.inc";

gate sx a {
    u2(-pi/2, pi/2) a;
}

gate sxdg a {
    s a;
    h a;
    s a;
}

gate xx_minus_yy(p0, p1) a, b {
    rz(-p1) b;
    sdg a;
    sx a;
    s a;
    s b;
    cx a, b;
    ry(0.5*p0) a;
    ry(-0.5*p0) b;
    cx a, b;
    sdg b;
    sdg a;
    sxdg a;
    s a;
    rz(p1) b;
}

gate rxx_custom(p0) a, b {
    h a;
    h b;
    cx a, b;
    rz(p0) b;
    cx a, b;
    h b;
    h a;
}

qreg q[5];

xx_minus_yy(4.938987693414485, 0.8049616944763924) q[0], q[3];

cu1(2.829858307545725) q[4], q[2];

rz(2.3297926977893746) q[1];

ry(4.763205750057398) q[4];

ch q[2], q[0];

x q[1];

ry(2.2275523539672073) q[3];

rxx_custom(4.291723147097387) q[4], q[2];

rx(4.679478635343389) q[0];

y q[3];

sx q[1];

u3(
    1.4257134880181992,
    4.208565449932414,
    2.746706513663991
) q[2];

y q[3];

rx(5.2318714070794075) q[4];

h q[0];

y q[1];