import numpy as np
from scipy.optimize import curve_fit

INIT_AMOUNT = 100.0

def get_init_amount():
    return INIT_AMOUNT

def get_bets_for_match_OLD(ovr1: int, ovr2: int):
    with open("files/inference_matches_test_out.txt", "r") as file:
        lines = [[float(x) for x in s.split()] for s in file.readlines()]

    #print(lines)

    left, right = 0, len(lines)
    diff = ovr1-ovr2
    for i in range(len(lines)):
        if diff < lines[i][0]:
            left = i-1
            right = i
            break

    if left <= -1:
        prob_w = lines[right][1]
        prob_d = lines[right][2]
        prob_l = lines[right][3]
    elif right >= len(lines):
        prob_w = lines[left][1]
        prob_d = lines[left][2]
        prob_l = lines[left][3]
    else:
        
        def calc_m_q(xa,xb, ya, yb):
            m = (yb-ya)/(xb-xa)
            q = yb - (m*xb)
            return m,q
        #print("left,right=", left, right)
        xa, xb = lines[left][0], lines[right][0]
        ya_w, yb_w = lines[left][1], lines[right][1]
        ya_d, yb_d = lines[left][2], lines[right][2]
        ya_l, yb_l = lines[left][3], lines[right][3]
        m, q = calc_m_q(xa,xb,ya_w,yb_w)
        prob_w = (m*diff) + q
        m, q = calc_m_q(xa,xb,ya_d,yb_d)
        prob_d = (m*diff) + q
        m, q = calc_m_q(xa,xb,ya_l,yb_l)
        prob_l = (m*diff) + q

    #print(prob_w, prob_d, prob_l, ", sum=", sum((prob_w, prob_d, prob_l)))
    return prob_w, prob_d, prob_l

def get_bets_for_match(ovr1: int, ovr2: int):
    diff = ovr1-ovr2

    with open("files/bets_bins.txt", "r") as file:
        lines = [[float(x) for x in s.split()] for s in file.readlines()]


    x_data  = [lines[i][0] for i in range(len(lines))]
    y_w = [lines[i][1] for i in range(len(lines))]
    y_d = [lines[i][2] for i in range(len(lines))]
    y_l = [lines[i][3] for i in range(len(lines))]

    def func(x, b,c):
        return 1/(1+(b*(np.exp(-c*x))))
        #return b*x + c

    def func_draw(x, a,b,c,o):
        return ( a * np.exp( (-1/2) * (((x-b)/c)**2) ) ) + o
    
    def func_draw_2(x, b,c):
        return 1/(1+(b*(np.exp(-c* np.abs(x)))))
    
    #plt.scatter(x_data, y_w, color="green", s=5)
    #plt.scatter(x_data, y_d, color="orange", s=5)
    #plt.scatter(x_data, y_l, color="red", s=5)

    popt_w, _ = curve_fit(func, x_data, y_w, p0=[1.8, 0.02])
    print("popt w=", popt_w)

    '''popt_d, _ = curve_fit(func_draw_2, x_data, y_d, p0=[1.8, -0.01])
    print("popt d=", popt_d)'''

    popt_l, _ = curve_fit(func, x_data, y_l, p0=[1.8, -0.02])
    print("popt l=", popt_l)

    prob_w = func(diff, popt_w[0], popt_w[1])
    #prob_d = func_draw_2(diff, popt_d[0], popt_d[1])
    prob_l = func(diff, popt_l[0], popt_l[1])
    prob_d = 1 - prob_w - prob_l

    #rr = np.arange(-650, 650, 1)
    #plt.plot(rr, func(rr, popt_w[0], popt_w[1]), color="lightgreen")
    #plt.plot(rr, func_draw_2(rr, popt_d[0], popt_d[1]), color="gold")
    #plt.plot(rr, func(rr, popt_l[0], popt_l[1]), color="pink")

    #plt.show()

    def calc_bet_payment(prob: float):
        div = 1
        offset = 0.0002
        res = div / ((prob+offset)**0.8)

        if res < 1.01:
            res = 1.01
        if res >= 10:
            res = round(res, 0)
        elif res >= 3:
            res = round(res, 1)
        else:
            res = round(res, 2)

        return res
    
    def calc_bet_payment_test(prob: float) -> float:
        if prob <= 0:
            return 1001
        if prob >= 1:
            return 1.01
        return 1/prob


    print(f"probabilities for a match between {ovr1} and {ovr2} = [{prob_w}, {prob_d}, {prob_l}] (sum={prob_w+prob_d+prob_l})")
    print(f"bets for a match between {ovr1} and {ovr2} = [{calc_bet_payment(prob_w)}, {calc_bet_payment(prob_d)}, {calc_bet_payment(prob_l)}])")

    return calc_bet_payment(prob_w), calc_bet_payment(prob_d), calc_bet_payment(prob_l)