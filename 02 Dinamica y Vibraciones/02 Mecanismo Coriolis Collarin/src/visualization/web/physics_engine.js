/**
 * Continuum Lab — Classical Mechanics & Dynamical Systems
 * Module: physics_engine.js
 * Analytical Kinematics & Coriolis Vector Engine (Pure JavaScript ES6)
 */

export class CoriolisMechanismParams {
    constructor({
        L1 = 1.0,           // Longitud manivela O1-A [m]
        d = 1.5,            // Distancia entre pivotes O1 y O2 [m]
        omega1 = 2.0,       // Velocidad angular manivela [rad/s]
        alpha1 = 0.0,       // Aceleracion angular manivela [rad/s^2]
        armExtension = 1.7, // Extension de la barra ranurada
        xO1 = 0.0,
        yO1 = 0.0
    } = {}) {
        this.L1 = L1;
        this.d = d;
        this.omega1 = omega1;
        this.alpha1 = alpha1;
        this.armExtension = armExtension;
        this.xO1 = xO1;
        this.yO1 = yO1;
    }

    get xO2() { return this.xO1; }
    get yO2() { return this.yO1 - this.d; }
    get isOscillating() { return this.d > this.L1; }
}

export class CoriolisPhysicsEngine {
    constructor(params = new CoriolisMechanismParams()) {
        this.params = params;
    }

    solve(theta1, time = 0.0) {
        const p = this.params;
        const L1 = p.L1;
        const w1 = p.omega1;
        const a1 = p.alpha1;

        // 1. Manivela (Punto A)
        const cos1 = Math.cos(theta1);
        const sin1 = Math.sin(theta1);

        const xA = p.xO1 + L1 * cos1;
        const yA = p.yO1 + L1 * sin1;

        const vxA = -L1 * w1 * sin1;
        const vyA = L1 * w1 * cos1;

        const axA = -L1 * (w1 * w1) * cos1 - L1 * a1 * sin1;
        const ayA = -L1 * (w1 * w1) * sin1 + L1 * a1 * cos1;

        // 2. Vector relativo desde pivote fijo O2 hacia collarin A
        const rx = xA - p.xO2;
        const ry = yA - p.yO2;
        const r2 = Math.sqrt(rx * rx + ry * ry);
        const theta2 = Math.atan2(ry, rx);

        const cos2 = Math.cos(theta2);
        const sin2 = Math.sin(theta2);

        // Vectores unitarios radial (ur) y transversal (ut)
        const ur = [cos2, sin2];
        const ut = [-sin2, cos2];

        // 3. Velocidades relativas
        // v_rel = vA . ur
        // omega2 = (vA . ut) / r2
        const v_rel = vxA * ur[0] + vyA * ur[1];
        const omega2 = (vxA * ut[0] + vyA * ut[1]) / r2;

        const v_rel_vec = [v_rel * ur[0], v_rel * ur[1]];
        const v_trans_vec = [omega2 * r2 * ut[0], omega2 * r2 * ut[1]];

        // 4. Aceleraciones y termino de Coriolis
        const a_dot_ur = axA * ur[0] + ayA * ur[1];
        const a_dot_ut = axA * ut[0] + ayA * ut[1];

        // Despejes analiticos
        const a_rel = a_dot_ur + (omega2 * omega2) * r2;
        const alpha2 = (a_dot_ut - 2.0 * omega2 * v_rel) / r2;

        // Vector aceleracion de Coriolis: 2 * (omega2 x v_rel) = (2 * omega2 * v_rel) * ut
        const a_cor_mag = 2.0 * omega2 * v_rel;
        const a_cor_vec = [a_cor_mag * ut[0], a_cor_mag * ut[1]];

        // Aceleracion centrifuga/centripeta de arrastre: -(omega2^2 * r2) * ur
        const a_cent_vec = [-(omega2 * omega2 * r2) * ur[0], -(omega2 * omega2 * r2) * ur[1]];

        // Aceleracion tangencial / Euler: (alpha2 * r2) * ut
        const a_euler_vec = [(alpha2 * r2) * ut[0], (alpha2 * r2) * ut[1]];

        // Aceleracion relativa: a_rel * ur
        const a_rel_vec = [a_rel * ur[0], a_rel * ur[1]];

        // Verificacion vectorial: a_rec = a_euler + a_cent + a_cor + a_rel
        const ax_rec = a_euler_vec[0] + a_cent_vec[0] + a_cor_vec[0] + a_rel_vec[0];
        const ay_rec = a_euler_vec[1] + a_cent_vec[1] + a_cor_vec[1] + a_rel_vec[1];
        const err = Math.sqrt((axA - ax_rec) ** 2 + (ayA - ay_rec) ** 2);

        // Extremo de la barra ranurada
        const armLength = Math.max(L1 + p.d, r2 * 1.3) * p.armExtension * 0.7;
        const tipX = p.xO2 + armLength * ur[0];
        const tipY = p.yO2 + armLength * ur[1];

        // Stylus decorativo para trazo hipnotico en la punta de la barra
        const stylusLength = armLength * 1.15;
        const stylusX = p.xO2 + stylusLength * ur[0];
        const stylusY = p.yO2 + stylusLength * ur[1];

        return {
            time,
            theta1,
            omega1: w1,
            rA: [xA, yA],
            vA: [vxA, vyA],
            aA: [axA, ayA],
            rO1: [p.xO1, p.yO1],
            rO2: [p.xO2, p.yO2],
            r2,
            theta2,
            ur,
            ut,
            v_rel,
            omega2,
            alpha2,
            a_rel,
            v_rel_vec,
            v_trans_vec,
            a_cor_mag,
            a_cor_vec,
            a_cent_vec,
            a_euler_vec,
            a_rel_vec,
            err,
            tip: [tipX, tipY],
            stylus: [stylusX, stylusY]
        };
    }
}
