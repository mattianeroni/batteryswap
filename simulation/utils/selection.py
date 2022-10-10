import math 
import random 




def biased_randomised_selection(options, beta=0.4):
    """
    The selection is made using a quasi-geometric function:

                f(x) = (1 - beta)^x


    :param options: A sequence of possible options.
    :param beta: The parameter of the geometric function.
    :return: The selected option.
    """
    idx = int(math.log(random.random(), 1.0 - beta)) % len(options)
    return options[idx]



OPTIONS = {
    "biased_randomised_selection" : biased_randomised_selection,
    "choice" : random.choice
}
