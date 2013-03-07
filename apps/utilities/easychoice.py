class EasyChoice(object):
    """
        Takes a key and value and tags them as id and value, such as EasyChoice(mychoice=1, 'My val'). 
    """
    def __init__(self, label=None, **kwargs):
        assert(len(kwargs) == 1)
        for k, v in kwargs.items():
            self.id = k
            self.v = v
        self.label = label or self.id

class EasyChoices(object):
    """
        Works with lists of K objects to get choice sets that are referenced with their values rather than their keys.
        e.g.
        MYSTUFF = EasyChoices(
            EasyChoice(something=0, label='Physical Address'),
            EasyChoice(else=1, label='Billing Address'),
        )
        
        You can say MYSTUFF.something to get 0. You can say MYSTUFF.choices() to get a data structure that can be given to a ChoiceField.
    """
    def __init__(self, *args):
        self.klist = args
        for k in self.klist:
            setattr(self, k.id, k.v)

    def choices(self):
        return [(k.v, k.label) for k in self.klist]

    def display(self, k):
        for ks in self.klist:
            if k==ks.v: return ks.label
        return ""

    def __getitem__(self,k):
        return self.display(k)