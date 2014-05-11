import BTrees.LOBTree
import BTrees.OLBTree
import BTrees.OOBTree
import persistent

class GenerationalSet(persistent.Persistent):

    def __init__(
        self,
        id=None,
        parent=None,
        maximum_removals=99,
        superset=False,
        id_attribute='id',
        ):
        self.id = id
        self.parent = parent
        self.maximum_removals = maximum_removals
        self.superset = superset
        self.id_attribute = id_attribute
        self.contents = BTrees.LOBTree.BTree()    # {generation -> ob}
        self.generations = BTrees.OLBTree.BTree() # {id -> generation}
        self.removals = BTrees.LOBTree.BTree()    # {generation -> id}
        if parent is not None:
            self.generation = parent.generation
        else:
            self.generation = 1

    def get_id(self, ob):
        return getattr(ob, self.id_attribute)

    def _updated(self):
        if self.parent is not None:
            self.parent.add(self)
            self.generation = self.parent.generation
        else:
            self.generation += 1
            notify(self)

    def add(self, ob, id=None):
        if id is None:
            id = self.get_id(ob)
        generation = self.generations.get(id, None)
        if generation is not None:
            self.contents.pop(generation, None)
            self.removals.pop(generation, None)
        self._updated()
        self.contents[self.generation] = ob
        self.generations[id] = self.generation

    def remove(self, ob, id=None):
        if id is None:
            id = self.get_id(ob)
        generation = self.generations[id]
        self.contents.pop(generation)
        self._updated()

        removals = self.removals
        removals[self.generation] = id
        self.generations[id] = self.generation

        while len(removals) > self.maximum_removals:
            ob = removals.pop(removals.minKey())
            self.generations.pop(id)

    def __getitem__(self, id):
        generation = self.generations[id]
        return self.contents[generation]

    def __len__(self):
        return len(self.contents)

    def __iter__(self):
        return iter(self.contents.values())

    def values(self, minimim_generation):
        return self.contents.values(minimim_generation)

    def __contains__(self, ob):
        try:
            id = self.get_id(ob)
        except AttributeError:
            id = ob
        generation = self.generations.get(id, None)
        return generation is not None and generation in self.contents

    def generational_updates(self, generation, subset=False):
        result = {}
        if subset:
            result['id'] = self.id
        else:
            result['generation'] = self.generation

        if generation >= self.generation:
            return result # common short circuit

        if (len(self.removals) >= self.maximum_removals and
            generation < self.removals.minKey()
            ):
            result['contents'] = (
                [subset.generational_updates(generation, True)
                 for subset in self.contents.values()]
                if self.superset
                else list(self.contents.values())
            )
        else:
            adds = self.contents.values(generation+1)
            adds = ([subset.generational_updates(generation, True)
                     for subset in adds]
                    if self.superset
                    else list(adds)
            )
            if adds:
                result['adds'] = adds

            removals = list(self.removals.values(generation+1))
            if removals:
                result['removals'] = removals

        return result

GSet = GenerationalSet

class StringIdGenerationalSet(GenerationalSet):
    "A set in which ids are stringified. This helps with long integer ids"
    def get_id(self, ob):
        return str(super(StringIdGenerationalSet, self).get_id(ob))

SGSet = StringIdGenerationalSet

class ValueGenerationalSet(GenerationalSet):
    "A set in which items are their own ids.  They must be orderable."
    def get_id(self, ob):
        return ob

VGSet = ValueGenerationalSet

def notify(s):
    "Replace me to be notified."
