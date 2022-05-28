using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class RiddleManager1 : MonoBehaviour
{
    public List<string> riddleNames;
    public List<bool> riddlesDone;
    public List<GameObject> visualisationsGameObjects;
    public List<Vector3> visualisationsPositions;
    public List<bool> instantiatedVisualisations;

    public bool allRiddlesComplete = false;

    List<GameObject> instantiatedVis = new List<GameObject>();
    float time = 0f;


    private void Update()
    {
        time += Time.deltaTime;
        Debug.Log(time);
        //180 seconds, not 20
        if(time > 20 && riddlesDone[0] == false && instantiatedVisualisations[0] == false)
        {
            instantiatedVis.Add(Instantiate(visualisationsGameObjects[0], visualisationsPositions[0], Quaternion.identity));
            instantiatedVisualisations[0] = true;
            time = 0;
        }
        if(time > 20 && riddlesDone[0] == true && riddlesDone[1] == false && instantiatedVisualisations[1] == false)
        {
            instantiatedVis.Add(Instantiate(visualisationsGameObjects[1], visualisationsPositions[1], Quaternion.identity));
            instantiatedVisualisations[1] = true;
            time = 0;
        }
        if (time > 20 && riddlesDone[0] == true && riddlesDone[1] == true && riddlesDone[2] == false && instantiatedVisualisations[2] == false)
        {
            instantiatedVis.Add(Instantiate(visualisationsGameObjects[2], visualisationsPositions[2], Quaternion.identity));
            instantiatedVisualisations[2] = true;
        }
    }

    public void setRiddleDone(int index)
    {
        riddlesDone[index] = true;

        if(instantiatedVis[index] != null)
        {
            destroyObjAfterSeconds(instantiatedVis[index]);
        }
        
        if(index == 2)
        {
            if(riddlesDone[0] == true && riddlesDone[1] == true)
            {
                allRiddlesComplete = true;
            }
        }
    }

    private IEnumerator destroyObjAfterSeconds(GameObject desotryObj)
    {
        yield return new WaitForSeconds(20);
        Destroy(desotryObj);
    }
}
