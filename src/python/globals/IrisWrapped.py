"""
    A Quick experiment in wrapping the Iris Native interface in a more Pythonic style.
    Example Usage:
        with IrisConnection(ip=..., port=... etc) as con:
            my_glob = IrisGlobal(con, "^MyGlob")
            print(my_glob[1,2,3])
            with con.transaction() as tran:
                my_glob[1,2,3] = 42
"""
import sys
import time
import argparse
from collections import deque
import irisnative


class IrisSlicer(object):
    """
    IrisSlicer represents a single Iris Global just like IrisGlobal does, except that this IrisSlicer provides higher
    level semantic operations in a separate class, so that IrisGlobal doesn't become overly complex and slow because of
    the complexity of argument parsing in low level operations like [].
    IrisSlicer is constructed from an IrisGlobal.slicer() call.
    usage:  my_slicer = IrisGlobal(IrisConnection(), ""MyGlob").slicer()
            dict = my_slicer[start:end:step, start:end:step ...]
    """
    def __init__(self, iris_global):
        self.iris_global = iris_global

    def __getitem__(self, keys=None):
        """Support for "value = my_global[slice, slice, ...]" syntax."""
        if type(keys) is not tuple:     # Single value/slice becomes tuple(x, )
            keys = tuple(keys,)
        iris_global = self.iris_global

        def iter_sub(prefix, next_keys):
            this_slice = next_keys[0]
            if type(this_slice) is slice:
                for this_key, this_value in iris_global.iteritems(key=prefix, reverse=False, start_from=this_slice.start):
                    if this_slice.stop is not None:
                        this_full_key = prefix + (type(this_slice.stop)(this_key),)
                        data = iris_global.data(this_full_key)
                        if IrisGlobal.data_has_value(data):
                            if this_full_key[-1] >= this_slice.stop:
                                break
                            yield this_full_key, this_value
                    else:
                        this_full_key = prefix + (this_key,)
                        data = iris_global.data(this_full_key)
                        if IrisGlobal.data_has_value(data):
                            yield this_full_key, this_value
                    if IrisGlobal.data_has_child(data) and len(next_keys) > 1:
                        yield from iter_sub(this_full_key, next_keys[1:])
            else:
                # Assume this_slice is specific value instead if being an actual slice.
                this_key = (() if prefix is None else prefix) + (this_slice,)
                data = iris_global.data(this_key)
                if IrisGlobal.data_has_value(data):
                    yield this_key, iris_global[this_key]
                if IrisGlobal.data_has_child(data) and len(next_keys) > 1:
                    yield from iter_sub(this_key, next_keys[1:])

        return {key: value for key, value in iter_sub((), keys)}


class IrisConnectionException(Exception):
    """Represents a failure to connect to IRIS"""


class IrisTransaction(object):
    """
    Supports Syntax like:
                with con.transaction() as tran:
                    my_glob[1, 2, 3] = 42
                    break                # Breaks out and Auto-commits transaction.
                    tran.commit()        # Breaks out and commits transaction
                    tran.rollback_one()  # Breaks out and rollback_one's tran
                    tran.rollback_all()  # Breaks out and rollback_all's tran
    """
    class BreakingGood(Exception):
        pass    # breaking out of with, via commit.

    class BreakingBad(Exception):
        pass    # breaking out of with, via rollback_one.

    class BreakingReallyBad(Exception):
        pass    # breaking out of with, via rollback_all.

    def __init__(self, iris, trans_depth):
        self.iris = iris
        self.trans_depth = trans_depth

    def __enter__(self):
        """Implements "with con.start_transaction as trans:" syntax."""
        self.iris.iris.tStart()
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):
        """Decide how we're wrapping up the transaction"""
        self.iris.pop_transaction()
        if ex_type in (None, IrisTransaction.BreakingGood):
            self.iris.iris.tCommit()
            return True     # commit() called. Commit the transaction and suppress this exception.
        if ex_type is IrisTransaction.BreakingBad:
            self.iris.iris.tRollbackOne()
            return True     # rollback_one() called. Rollback the transaction and suppress this exception.
        if ex_type is not IrisTransaction.BreakingReallyBad:
            self.iris.iris.tRollbackOne()
            return False    # Unexpected exception: Rollback one level and throw exception to the keeper.

        # rollback_all() called. Full rollback already done.
        if self.trans_depth == 0:
            return True     # Suppress  exception at base transaction level.
        return False        # Propagate exception at higher transaction levels.

    def commit(self):
        raise self.BreakingGood

    def rollback_one(self):
        raise self.BreakingBad

    def rollback_all(self):
        self.iris.iris.tRollback()
        raise self.BreakingReallyBad


class IrisGlobal(object):
    """
    IrisGlobal represents a single Iris Global of name 'global_name', accessed via a connection 'iris'
        usage:  my_glob = IrisGlobal(iris, "^MyGlob")       # Prepare to use an Iris global named ^MyGlob. Equivalent to iris.MyGlob
                my_glob.name()                              # -> "^MyGlob"
                my_glob[None] = 42                          # set ^MyGlob = 42
                x = my_glob[None]                           # set x = ^MyGlob           except x is in Python
                my_glob[1,2,3] = 42                         # set ^MyGlob(1,2,3) = 42
                tup = (1,2,3)
                my_glob[*tup] = 42                          # set ^MyGlob(1,2,3) = 42
                x = my_glob[1,2,3]                          # set x = ^MyGlob(1,2,3)    except x is in Python
                x = my_glob(1,2,3)                          # set x = ^MyGlob(1,2,3)    except x is in Python
                del my_glob[1,2,3]                          # kill ^MyGlob(1,2,3)       Python style
                my_glob.kill((1,2,3))                       # kill ^MyGlob(1,2,3)       Closer to Object Script style
                for k,v in my_glob.iteritems()              # $Order iterate key,value pairs at root of ^MyGlob
                for k,v in my_glob.iteritems(reverse=True)  # $Order iterate in reverse
                for k,v in my_glob.iteritems(key=(1,2),     # $Order iterate in subscripts below (1,2),
                                             start_from=1)  #                   starting from (1,2,1).
                for k   in my_glob.iterkeys((1,2))          # $Order iterate key             below subroot of [1,2]
                for v   in my_glob.itervalues((1,))         # $Order iterate value           at root of ^MyGlob
                my_glob.increment((1,2), 1)                 # $Increment(^MyGlob(1,2))
                my_glob.lock((1,2,3))                       # lock ^MyGlob(1,2,3)
                my_glob.unlock((1,2,3))                     # unlock ^MyGlob(1,2,3)
                my_glob.has_child((1,2,3))                  # $Data(^MyGlob(1,2,3)) = 10 or 11
                my_glob.has_value((1,2,3))                  # $Data(^MyGlob(1,2,3)) = 1  or 11
    """
    def __init__(self, iris, global_name):
        self.global_name = global_name
        if not iris.is_open():
            raise Exception("IRIS Connection not open")
        self.iris = iris.iris

    def name(self):
        """The string name of this global."""
        return self.global_name

    def slicer(self):
        """Returns an IrisSlicer object based on this IrisGlobal"""
        return IrisSlicer(self)

    def _key_params(self, key):
        """Standardised evaluation of subscripts, passed as None, singleValue or (tuple)"""
        return (self.global_name, *key) if type(key) is tuple else\
               (self.global_name,) if key is None else\
               (self.global_name, key)

    def _value_key_params(self, value, key):
        """Standardised evaluation of value, subscripts, passed as None, singleValue or (tuple)"""
        return (value, self.global_name, *key) if type(key) is tuple else\
               (value, self.global_name,) if key is None else\
               (value, self.global_name, key)

    def has_child(self, key=None):
        """Does global[subscript] have subordinate subscripts."""
        return self.iris.isDefined(*self._key_params(key)) in (10, 11)

    def has_value(self, key=None):
        """Does global[subscript] have a value"""
        return self.iris.isDefined(*self._key_params(key)) in (1, 11)

    def data(self, key=None):
        """Gets the $Data(global) value"""
        return self.iris.isDefined(*self._key_params(key))

    @staticmethod
    def data_has_child(data):
        """Evaluates the $Data(global) value to tell if there are any child subscripts in the global."""
        return data in (10, 11)

    @staticmethod
    def data_has_value(data):
        """Evaluates the $Data(global) value to tell if this global subscript has a value."""
        return data in (1, 11)

    def __getitem__(self, key=None):
        """Support for "value = my_global[subscripts]" syntax."""
        return self.iris.get(*self._key_params(key))

    def __setitem__(self, key=None, value=None):
        """Support for "my_global[subscripts] = value" syntax."""
        try:
            self.iris.set(*self._value_key_params(value, key))
        except Exception as e:
            print(repr(e))

    def __delitem__(self, key=None):
        """Support for "del my_global[subscripts]" syntax."""
        return self.iris.kill(*self._key_params(key))

    def kill(self, key=None):
        """Kill my_global[subscripts]. Same effect as del my_global[subscripts]."""
        self.__delitem__(key)

    def increment(self, key=None, value=1):
        """my_global[subscripts] += value, as an atomic action."""
        return self.iris.increment(*self._value_key_params(value, key))

    def lock(self, key=None, lock_mode="", timeout=1):
        """ lock my_global[subscripts]
            lock_mode = "S"hared, "E"scalating or "SE",
            timeout is seconds
        """
        self.iris.lock(lock_mode, timeout, *self._key_params(key))

    def unlock(self, key=None, lock_mode=""):
        """ Unlock my_global[subscripts]
            lock_mode="I"mmed, "D"efer, "S"hare, "E"scalate or "SE"
        """
        self.iris.unlock(lock_mode, *self._key_params(key))

    def __call__(self, *args):
        """Support for "value = my_global(subscripts)" syntax."""
        return self.__getitem__(args)

    @staticmethod
    def iteritems_int_key(item_iter):
        for k, v in item_iter:
            yield int(k), v

    @staticmethod
    def iterkeys_int_key(key_iter):
        for k in key_iter:
            yield int(k)

    def iterkeys(self, key=None, reverse=False, start_from=None, int_key=False):
        """Iterate through keys at my_global(subscript), optionally after a value, or in reverse"""
        key_iter = self.iris.iterator(*self._key_params(key)).subscripts().startFrom(start_from)
        key_iter = key_iter.reversed() if reverse else key_iter
        return IrisGlobal.iterkeys_int_key(key_iter) if int_key else key_iter

    def itervalues(self, key=None, reverse=False, start_from=None):
        """Iterate through values at my_global(subscript), optionally after a value, or in reverse"""
        value_iter = self.iris.iterator(*self._key_params(key)).values().startFrom(start_from)
        return value_iter.reversed() if reverse else value_iter

    def iteritems(self, key=None, reverse=False, start_from=None, int_key=False):
        """Iterate through (key,value) at my_global(subscript), optionally after a value, or in reverse"""
        item_iter = self.iris.iterator(*self._key_params(key)).items().startFrom(start_from)
        item_iter = item_iter.reversed() if reverse else item_iter
        return IrisGlobal.iteritems_int_key(item_iter) if int_key else item_iter

    def iter_all(self, key=None):
        """Depth first iterator through all (key,value), at and below 'key'."""
        iter_stack = deque()
        key = key if type(key) is tuple else tuple() if key is None else tuple(key)
        if self.has_value(key):
            yield key, self(*key)
        iter_stack.append((key, self.iris.iterator(*self._key_params(key)).items()))
        while iter_stack:
            try:
                k, v = next(iter_stack[-1][1])
                try:
                    k = int(k)
                except ValueError:
                    pass
                key = tuple((*iter_stack[-1][0], k))
                yield key, v
                if self.has_child(key):
                    iter_stack.append((key, self.iris.iterator(*self._key_params(key)).items()))
            except StopIteration:
                iter_stack.pop()


class Iris(object):
    """
        Iris represents a connection to an Iris database
            usage:  try:
                        with Iris() as iris:
                            my_glob = IrisGlobal(iris, "^MyGlob")    # or just iris.MyGlob
                            # Do various DB operations.
                            with iris.transaction() as tran:
                                my_glob[1,2,3] = 42

                                tran.rollback_one()     # Breaks out and rollback_one's tran
                                tran.rollback_all()     # Breaks out and rollback_all's tran
                                tran.commit()           # Breaks out and commits transaction

                                my_glob[1,2,4] = 43     # This won't happen

                    except IrisConnectionException as e:
                        print(repr(e))
    """
    def __init__(self,
                 ip="127.0.0.1", port=51791,
                 namespace="User", username="_SYSTEM", password="SYS",
                 timeout=10000, shared_memory=True, logfile=""):

        # Initially, no transaction is started.
        self.trans = deque()

        # Make connection to InterSystems IRIS database
        #try:
        self.iris_connection = irisnative.createConnection(hostname=ip, port=port, namespace=namespace,
                                                           username=username, password=password,
                                                           timeout=timeout, sharedmemory=shared_memory, logfile=logfile)
        #except Exception as e:
        #    self.iris_connection = None
        #    self.iris = None
        #    raise IrisConnectionException(repr(e))

        if self.iris_connection.isClosed():
            self.iris_connection = None
            self.iris = None
            raise IrisConnectionException("irisnative.createConnection() - Failed to create open connection.")

        # Create an InterSystems IRIS native object
        try:
            self.iris = irisnative.createIris(self.iris_connection)
        except Exception as e:
            self.iris_connection.close()
            self.iris_connection = None
            self.iris = None
            raise IrisConnectionException(repr(e))

    def __getattribute__(self, name) -> IrisGlobal:
        """Implement iris.<globalname>"""
        try:
            attr = object.__getattribute__(self, name)
        except AttributeError:
            try:
                # Make a new attribute for the global name.
                object.__getattribute__(self, "iris")  # This will throw AttributeError if we're not constructed.
                object.__setattr__(self, name, IrisGlobal(self, "^"+name))
                attr = object.__getattribute__(self, name)
            except AttributeError as _e:
                raise
        return attr

    def __getitem__(self, name) -> IrisGlobal:
        """Implement iris["<globalname>"]"""
        try:
            attr = object.__getattribute__(self, name)
        except AttributeError:
            object.__setattr__(self, name, IrisGlobal(self, "^"+name))
            attr = object.__getattribute__(self, name)
        return attr

    def __enter__(self):
        """__enter__() and __exit__() support "with Iris() as iris:" syntax."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """__enter__() and __exit__() support "with Iris() as iris:" syntax."""
        self.unlock_all()
        self.close()

    def is_open(self):
        """Is the connection to Iris open and nowhere to go."""
        return self.iris is not None and self.iris_connection is not None and not self.iris_connection.isClosed()

    def using_shared_memory(self):
        """Is the connection to Iris using shared memory?"""
        return self.is_open() and self.iris_connection.isUsingSharedMemory()

    def close(self):
        """We need better ways ti """
        self.iris_connection.close()

    def unlock_all(self):
        self.iris.releaseAllLocks()

    def transaction(self):
        trans = IrisTransaction(self, len(self.trans))
        self.trans.append(trans)
        return trans

    def pop_transaction(self):
        self.trans.pop()


def blah_iris_simple():
    parser = argparse.ArgumentParser(description="Simple Test IrisWrapped.")
    parser.add_argument("-i", "--ip", help="IP Address", type=str, default="127.0.0.1")
    parser.add_argument("-p", "--port", help="IP Port", type=int, default=51791)
    parser.add_argument("-n", "--namespace", help="Namespace", type=str, default="User")
    parser.add_argument("-u", "--username", help="User Name", type=str, default="_SYSTEM")
    parser.add_argument("-w", "--password", help="Password", type=str, default="SYS")
    args = parser.parse_args()
    try:
        with Iris(ip=args.ip, port=args.port, namespace=args.namespace,
                  username=args.username, password=args.password) as iris:
            my_glob = iris.MyGlob               # Reference to Iris global ^MyGlob.
            with iris.transaction() as tran:    # Start transaction.
                my_glob[1, 2, 3] = 42
                tran.commit()                   # Commits transaction, break with.
                my_glob[1, 2, 4] = 43           # This won't happen.

            print(my_glob[1, 2, 3])             # Print subscript-ed global.

    except IrisConnectionException as e:        # Deal with failure to connect.
        print(repr(e))


def blah_iris_wrapped():
    parser = argparse.ArgumentParser(description="Testing IrisWrapped.")
    parser.add_argument("-i", "--ip", help="Iris IP Address", type=str, default="127.0.0.1")
    parser.add_argument("-p", "--port", help="Iris IP Port", type=int, default=51795)
    parser.add_argument("-n", "--namespace", help="Iris Namespace", type=str, default="USER")
    parser.add_argument("-u", "--username", help="Iris User Name", type=str, default="_SYSTEM")
    parser.add_argument("-w", "--password", help="Iris Password", type=str, default="SYS")
    args = parser.parse_args()
    try:
        with Iris(ip=args.ip, port=args.port, namespace=args.namespace, username=args.username, password=args.password) as iris:

            print("iris.using_shared_memory() =", iris.using_shared_memory())

            iris.MyGlob[None] = 4242

            print("\nSetting Globals:")
            global_set = ((1,         42),
                          (42,        1000),
                          ((1, 2, 2), "String"),
                          ((1, 2, 3), 123),
                          ((1, 2, 4), 123.456),
                          ((1, 2, 5), ""),
                          ((1, 2, 7), 127),
                          ("String",  2))
            for sub, val in global_set:
                iris.MyGlob[sub] = val
                print("    {}({}) = {}".format(iris.MyGlob.name(), sub, iris.MyGlob[sub]))

            print("\nKilling Globals:")
            global_del = ((1, 2, 7), )
            for key in global_del:
                del iris.MyGlob[key]
                print("    {}({})".format(iris.MyGlob.name(), key))

            print("\nChecking Globals Values and Node Status")
            for sub, val in global_set:
                print("    {}({:>9s}) = {:>8s}, has_value={:>5s}, has_child={:>5s}"
                      .format(iris.MyGlob.name(), repr(sub), repr(iris.MyGlob[sub]),
                              repr(iris.MyGlob.has_value(sub)), repr(iris.MyGlob.has_child(sub))))

            """ Experimental slicer API
            print("\nExercising slicer on ^MyGlob")
            my_glob = iris.MyGlob
            my_slicer = my_glob.slicer()
            # print("\nmy_slicer[1, 2, 0:7]")
            # for k, v in my_slicer[1, 2, 0:7].items():
            #     print("    ", k, ":", repr(v))
            print("\nmy_slicer['':, '':, '':]")
            for k, v in my_slicer[0:99, 0:, 0:].items():
                print("    ", k, ":", repr(v))
            raise Exception("Early Exit")
            """

            print("\nIterate Items ():")
            for sub, val in iris.MyGlob.iteritems():
                print("    {}({:>9s}) = {:>8s}".format(iris.MyGlob.name(), repr(sub), repr(val)))

            key = (1, 2)
            print("\nIterate Keys (1,2):")
            for sub in iris.MyGlob.iterkeys(key=key):
                print("    {}({})".format(iris.MyGlob.name(), (*key, int(sub))))

            print("\nIterate Values (1,2):")
            for idx, val in enumerate(iris.MyGlob.itervalues(key=key)):
                print("    {}({})[{}] = {:>8s}".format(iris.MyGlob.name(), repr(key), idx, repr(val)))

            print("\nIterate Items (1,2):")
            for sub, val in iris.MyGlob.iteritems(key=key):
                print("    {}({}) = {:>8s}".format(iris.MyGlob.name(), (*key, int(sub)), repr(val)))

            print("\nIterate Items (1,2), in reverse:")
            for sub, val in iris.MyGlob.iteritems(key=key, reverse=True):
                print("    {}({}) = {:>8s}".format(iris.MyGlob.name(), (*key, int(sub)), repr(val)))

            print("\nIterate Items (1,2), in reverse, after '5':")
            for sub, val in iris.MyGlob.iteritems(key=key, reverse=True, start_from=5):
                print("    {}({}) = {:>8s}".format(iris.MyGlob.name(), (*key, int(sub)), repr(val)))

            # Test Transactions
            print("\nTransaction Tests:")
            for tn in range(20):  # Clean out test space in global.
                del iris.MyGlob[2, tn]

            print("    One level transaction - {:20s}: ".format("Commit"), end="")
            with iris.transaction() as trans:
                iris.MyGlob[2, 1] = 21
                trans.commit()
            if iris.MyGlob[2, 1] == 21:
                print("Success.")
            else:
                print("Failed.")

            print("    One level transaction - {:20s}: ".format("Default Commit:"), end="")
            with iris.transaction():
                iris.MyGlob[2, 2] = 22
            if iris.MyGlob[2, 2] == 22:
                print("Success.")
            else:
                print("Failed.")

            print("    One level transaction - {:20s}: ".format("Rollback"), end="")
            with iris.transaction() as trans:
                iris.MyGlob[2, 3] = 23
                trans.rollback_one()
            if iris.MyGlob.has_value((2, 3)):
                print("Failed:", iris.MyGlob[2, 3])
            else:
                print("Success.")

            print("    One level transaction - {:20s}: ".format("Rollback All"), end="")
            with iris.transaction() as trans:
                iris.MyGlob[2, 4] = 24
                trans.rollback_all()
            if iris.MyGlob.has_value((2, 4)):
                print("Failed:", iris.MyGlob[2, 4])
            else:
                print("Success.")

            print("    Two level transaction - {:20s}: ".format("Commits"), end="")
            with iris.transaction() as trans1:
                iris.MyGlob[2, 5] = 25
                with iris.transaction() as trans2:
                    iris.MyGlob[2, 6] = 26
                    trans2.commit()
                trans1.commit()
            if iris.MyGlob[2, 5] == 25 and iris.MyGlob[2, 6] == 26:
                print("Success.")
            else:
                print("Failed.")

            print("    Two level transaction - {:20s}: ".format("Default Commits"), end="")
            with iris.transaction():
                iris.MyGlob[2, 7] = 27
                with iris.transaction():
                    iris.MyGlob[2, 8] = 28
            if iris.MyGlob[2, 7] == 27 and iris.MyGlob[2, 8] == 28:
                print("Success.")
            else:
                print("Failed.")

            print("    Two level transaction - {:20s}: ".format("Commit/Rollback"), end="")
            with iris.transaction():
                iris.MyGlob[2, 9] = 29
                with iris.transaction() as trans2:
                    iris.MyGlob[2, 10] = 210
                    trans2.rollback_one()
            if iris.MyGlob[2, 9] == 29 and not iris.MyGlob.has_value((2, 10)):
                print("Success.")
            else:
                print("Failed.")

            print("    Two level transaction - {:20s}: ".format("Commit/Rollback_all"), end="")
            with iris.transaction():
                iris.MyGlob[2, 11] = 211
                with iris.transaction() as trans2:
                    iris.MyGlob[2, 12] = 212
                    trans2.rollback_all()
            if not iris.MyGlob.has_value((2, 11)) and not iris.MyGlob.has_value((2, 12)):
                print("Success.")
            else:
                print("Failed.")

            print("    Two level transaction - {:20s}: ".format("Rollback/Commit"), end="")
            with iris.transaction() as trans1:
                iris.MyGlob[2, 13] = 213
                with iris.transaction() as trans2:
                    iris.MyGlob[2, 14] = 214
                    trans2.commit()
                trans1.rollback_one()
            if not iris.MyGlob.has_value((2, 13)) and not iris.MyGlob.has_value((2, 14)):
                print("Success.")
            else:
                print("Failed.")

            print("    Two level transaction - {:20s}: ".format("Rollback/Rollback"), end="")
            with iris.transaction() as trans1:
                iris.MyGlob[2, 13] = 213
                with iris.transaction() as trans2:
                    iris.MyGlob[2, 14] = 214
                    trans2.rollback_one()
                trans1.rollback_one()
            if not iris.MyGlob.has_value((2, 13)) and not iris.MyGlob.has_value((2, 14)):
                print("Success.")
            else:
                print("Failed.")

            print("    Two level transaction - {:20s}: ".format("Rollback_all/Commit"), end="")
            with iris.transaction() as trans1:
                iris.MyGlob[2, 13] = 213
                with iris.transaction() as trans2:
                    iris.MyGlob[2, 14] = 214
                    trans2.commit()
                trans1.rollback_all()
            if not iris.MyGlob.has_value((2, 13)) and not iris.MyGlob.has_value((2, 14)):
                print("Success.")
            else:
                print("Failed.")

            print("    Two level transaction - {:20s}: ".format("Out of order"), end="")
            with iris.transaction() as trans1:
                iris.MyGlob[2, 15] = 215
                with iris.transaction():
                    iris.MyGlob[2, 16] = 216
                    trans1.commit()
            if iris.MyGlob[2, 15] == 215 and iris.MyGlob[2, 16] == 216:
                print("Success.")
            else:
                print("Failed.")

            print("\nIterate ALL Items:")
            for sub, val in iris.MyGlob.iter_all():
                print("    "*len(sub), "    {}({}) = {:>8s}".format(iris.MyGlob.name(), sub, repr(val)))

            print("\nIterate ALL Items below (1,):")
            for sub, val in iris.MyGlob.iter_all((1,)):
                print("    "*(len(sub)-1), "    {}({}) = {:>8s}".format(iris.MyGlob.name(), sub, repr(val)))

            print("\nTime test:")
            perf_glob = iris.MyPerfGlob
            del perf_glob[None]

            it = 1000000
            t1 = time.time()
            for i in range(it):
                perf_glob[i] = i
            t2 = time.time()
            for i in range(it):
                _x = perf_glob[i]
            t3 = time.time()

            wt = t2 - t1
            print("    Over {} writes ... Write time {:4.2f} seconds or {:8.0f}/sec".format(it, wt, it/wt))

            rt = t3 - t2
            print("    Over {} reads  ... Read  time {:4.2f} seconds or {:8.0f}/sec".format(it, rt, it/rt))

    except IrisConnectionException as e:
        print(repr(e))
        print(args)

    except Exception as e:
        if type(e) is Exception:
            print("Exiting - ", repr(e))
            sys.exit(-1)
        raise


# Start event loop.
if __name__ == '__main__':
    blah_iris_wrapped()
    # blah_iris_simple()
